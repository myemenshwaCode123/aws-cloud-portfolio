import json
import boto3
import uuid
import os
import urllib.parse
from datetime import datetime, timezone
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client  = boto3.client('s3')
dynamodb   = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

TABLE_NAME        = os.environ['TABLE_NAME']
QUARANTINE_BUCKET = os.environ['QUARANTINE_BUCKET']
SNS_TOPIC_ARN     = os.environ['SNS_TOPIC_ARN']

table = dynamodb.Table(TABLE_NAME)


def put_cloudwatch_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='SilentScalper',
        MetricData=[{'MetricName': metric_name, 'Value': value, 'Unit': unit}]
    )


def send_sns_alert(subject, message):
    sns_client.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)


def process_file(content: str) -> dict:
    lines = content.strip().split('\n')
    processed_lines, error_lines = [], []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if any(char in line for char in ['<', '>', ';', '--']):
            error_lines.append({'line': i + 1, 'content': line, 'reason': 'Forbidden characters'})
        else:
            processed_lines.append(line.upper())

    return {
        'processed_lines': processed_lines,
        'error_lines': error_lines,
        'total_input': len(lines),
        'total_processed': len(processed_lines),
        'total_errors': len(error_lines)
    }


def lambda_handler(event, context):
    start_time = datetime.now(timezone.utc)

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        object_key    = urllib.parse.unquote_plus(record['s3']['object']['key'])
        file_id       = str(uuid.uuid4())
        processed_at  = start_time.isoformat()

        try:
            response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
            content  = response['Body'].read().decode('utf-8')
            result   = process_file(content)
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

            table.put_item(Item={
                'file_id': file_id, 'processed_at': processed_at,
                'source_bucket': source_bucket, 'object_key': object_key,
                'status': 'SUCCESS', 'total_input': result['total_input'],
                'total_processed': result['total_processed'],
                'total_errors': result['total_errors'], 'duration_ms': duration_ms
            })

            put_cloudwatch_metric('FilesProcessed', 1)
            put_cloudwatch_metric('ProcessingDurationMs', duration_ms, 'Milliseconds')

            if result['error_lines']:
                put_cloudwatch_metric('DataErrors', len(result['error_lines']))
                send_sns_alert(
                    f"⚠️ Silent Scalper: Data errors in {object_key}",
                    f"Errors found: {len(result['error_lines'])}\n{json.dumps(result['error_lines'][:5], indent=2)}"
                )

            logger.info(f"SUCCESS: {file_id} | {result['total_processed']} lines in {duration_ms}ms")

        except Exception as e:
            logger.error(f"FAILED: {object_key} | {str(e)}")
            try:
                s3_client.copy_object(
                    CopySource={'Bucket': source_bucket, 'Key': object_key},
                    Bucket=QUARANTINE_BUCKET,
                    Key=f"quarantine/{processed_at[:10]}/{object_key}"
                )
            except Exception as copy_err:
                logger.error(f"Quarantine copy failed: {copy_err}")

            table.put_item(Item={
                'file_id': file_id, 'processed_at': processed_at,
                'source_bucket': source_bucket, 'object_key': object_key,
                'status': 'FAILED', 'error_message': str(e)
            })

            put_cloudwatch_metric('ProcessingFailures', 1)
            send_sns_alert(
                f"🚨 Silent Scalper: Processing FAILED for {object_key}",
                f"Error: {str(e)}\nFile moved to quarantine for manual review."
            )

    return {'statusCode': 200, 'body': 'Processing complete'}
