# Project 3: Smart Vault — Automated Backup + Disaster Recovery

## Overview
A tag-driven, fully automated EBS backup system with cross-region disaster recovery. Every component — including the demo EC2 instance itself — is defined as Infrastructure as Code.

## Architecture

EventBridge (cron: 02:00 UTC daily)
↓
Lambda: discovers instances tagged backup=true
↓
Creates EBS snapshot (us-east-1)
↓
Copies snapshot to DR region (us-west-2)   ← cross-region disaster recovery
↓
Deletes snapshots older than retention window
↓
SNS report + CloudWatch metrics

## Key Engineering Decisions
- **Tag-based discovery**: Add/remove instances from backups by tagging alone — zero code changes.
- **Cross-region DR**: Protects against full-region outages, not just single-AZ failures.
- **No SSH keys**: Instance access via AWS Systems Manager Session Manager — no open ports, no key management, no key leakage risk.
- **No hardcoded AMI IDs**: Latest Amazon Linux AMI resolved dynamically via SSM Parameter Store at deploy time.
- **Fully IaC**: The entire stack, including the EC2 instance, deploys seamlessly with `sam deploy`.

## AWS Services

| Service | Purpose |
|---|---|
| **EC2 / EBS** | Compute + storage being protected |
| **Lambda** | Backup orchestration and synchronization |
| **EventBridge** | Cron scheduling for automation |
| **SNS** | Daily status reports + failure alerting |
| **CloudWatch** | Snapshot metrics tracking + operational alarms |
| **SSM** | Keyless, portless secure instance management |
| **AWS SAM** | Repeatable Infrastructure as Code deployment |

## Business Impact
- Eliminates human operational error from manual backup scheduling.
- Fully survives a total AWS region failure, keeping enterprise data resilient.
- Bounds and predicts cloud storage costs dynamically via automated retention enforcement.
