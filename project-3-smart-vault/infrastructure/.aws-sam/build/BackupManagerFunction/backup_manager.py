import boto3
import json
import os
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2        = boto3.client('ec2')
sns_client = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

SNS_TOPIC_ARN  = os.environ['SNS_TOPIC_ARN']
RETENTION_DAYS = int(os.environ.get('RETENTION_DAYS', '7'))
DR_REGION      = os.environ.get('DR_REGION', 'us-west-2')
SOURCE_REGION  = os.environ.get('AWS_REGION', 'us-east-1')
BACKUP_TAG_KEY, BACKUP_TAG_VALUE = 'backup', 'true'

ec2_dr = boto3.client('ec2', region_name=DR_REGION)


def put_cloudwatch_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='SmartVault',
        MetricData=[{'MetricName': metric_name, 'Value': value, 'Unit': unit}]
    )


def get_instances_to_backup():
    response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{BACKUP_TAG_KEY}', 'Values': [BACKUP_TAG_VALUE]},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
        ]
    )
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = next((t['Value'] for t in instance.get('Tags', []) if t['Key'] == 'Name'), 'unnamed')
            instances.append({
                'instance_id': instance['InstanceId'],
                'name': name,
                'volumes': [b['Ebs']['VolumeId'] for b in instance.get('BlockDeviceMappings', []) if 'Ebs' in b]
            })
    logger.info(f"Found {len(instances)} instances tagged for backup")
    return instances


def create_snapshot(volume_id, instance_name, instance_id):
    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y-%m-%dT%H-%M-%S')
    response = ec2.create_snapshot(
        VolumeId=volume_id,
        Description=f"SmartVault backup | {instance_name} | {instance_id} | {timestamp}",
        TagSpecifications=[{
            'ResourceType': 'snapshot',
            'Tags': [
                {'Key': 'Name', 'Value': f"backup-{instance_name}-{timestamp}"},
                {'Key': 'CreatedBy', 'Value': 'SmartVault'},
                {'Key': 'InstanceId', 'Value': instance_id},
                {'Key': 'InstanceName', 'Value': instance_name},
                {'Key': 'CreatedAt', 'Value': now.isoformat()},
            ]
        }]
    )
    snapshot_id = response['SnapshotId']
    logger.info(f"Created snapshot {snapshot_id} for volume {volume_id}")
    return snapshot_id


def copy_snapshot_to_dr(snapshot_id, instance_name):
    """Copy the snapshot to a second region for disaster recovery."""
    try:
        response = ec2_dr.copy_snapshot(
            SourceRegion=SOURCE_REGION,
            SourceSnapshotId=snapshot_id,
            Description=f"DR copy of {snapshot_id} for {instance_name}",
            TagSpecifications=[{
                'ResourceType': 'snapshot',
                'Tags': [
                    {'Key': 'CreatedBy', 'Value': 'SmartVault'},
                    {'Key': 'SourceSnapshot', 'Value': snapshot_id},
                    {'Key': 'DR', 'Value': 'true'}
                ]
            }]
        )
        dr_snapshot_id = response['SnapshotId']
        logger.info(f"DR copy created: {dr_snapshot_id} in {DR_REGION}")
        put_cloudwatch_metric('DRSnapshotsCreated', 1)
        return dr_snapshot_id
    except Exception as e:
        logger.error(f"DR copy failed for {snapshot_id}: {e}")
        put_cloudwatch_metric('DRCopyFailures', 1)
        return None


def delete_old_snapshots():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    response = ec2.describe_snapshots(Filters=[{'Name': 'tag:CreatedBy', 'Values': ['SmartVault']}], OwnerIds=['self'])
    deleted = 0
    for snapshot in response['Snapshots']:
        if snapshot['StartTime'].replace(tzinfo=timezone.utc) < cutoff_date:
            try:
                ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                deleted += 1
            except Exception as e:
                logger.error(f"Could not delete {snapshot['SnapshotId']}: {e}")
    return deleted


def lambda_handler(event, context):
    now = datetime.now(timezone.utc).isoformat()
    results = {'timestamp': now, 'snapshots_created': [], 'snapshots_deleted': 0, 'errors': []}
    logger.info("=== SmartVault Backup Run Starting ===")

    instances = get_instances_to_backup()

    for instance in instances:
        for volume_id in instance['volumes']:
            try:
                # 1. Trigger the primary snapshot creation
                snapshot_id = create_snapshot(volume_id, instance['name'], instance['instance_id'])
                
                # 2. Waiter Block: Pause execution until the source snapshot is fully 'completed'
                logger.info(f"Waiting for source snapshot {snapshot_id} to finish completing...")
                snapshot_waiter = ec2.get_waiter('snapshot_completed')
                snapshot_waiter.wait(
                    SnapshotIds=[snapshot_id],
                    WaiterConfig={'Delay': 15, 'MaxAttempts': 15}  # Checks every 15 seconds up to ~3.75 minutes
                )
                logger.info(f"Source snapshot {snapshot_id} is ready. Initiating cross-region copy to {DR_REGION}...")

                # 3. Copy the completed snapshot to the DR region
                dr_snapshot_id = copy_snapshot_to_dr(snapshot_id, instance['name'])
                
                results['snapshots_created'].append({
                    'snapshot_id': snapshot_id, 'volume_id': volume_id,
                    'instance': instance['name'], 'dr_snapshot_id': dr_snapshot_id
                })
                put_cloudwatch_metric('SnapshotsCreated', 1)
            except Exception as e:
                logger.error(f"Snapshot processing or DR copy failed for {volume_id}: {e}")
                results['errors'].append(str(e))
                put_cloudwatch_metric('SnapshotFailures', 1)

    try:
        results['snapshots_deleted'] = delete_old_snapshots()
        put_cloudwatch_metric('SnapshotsDeleted', results['snapshots_deleted'])
    except Exception as e:
        results['errors'].append(f"Cleanup error: {e}")

    subject = (f"⚠️ SmartVault: Backup completed WITH errors" if results['errors']
               else f"✅ SmartVault: {len(results['snapshots_created'])} snapshot(s) created + DR copied")

    message = (
        f"SmartVault Backup Report\n========================\n"
        f"Timestamp: {now}\nInstances backed up: {len(instances)}\n"
        f"Snapshots created: {len(results['snapshots_created'])}\n"
        f"DR region: {DR_REGION}\n"
        f"Snapshots deleted (>{RETENTION_DAYS}d old): {results['snapshots_deleted']}\n"
        f"Errors: {len(results['errors'])}\n"
    )
    sns_client.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
    logger.info("=== SmartVault Run Complete ===")

    return {'statusCode': 200, 'body': json.dumps(results, default=str)}
