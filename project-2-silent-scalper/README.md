# Project 2: Silent Scalper — Serverless Data Pipeline

## Overview
An event-driven serverless pipeline that processes files uploaded to S3, validates and
transforms data, stores results in DynamoDB, quarantines bad files automatically, and
exposes results through a live dashboard — fully defined as Infrastructure as Code.

## Architecture
![Architecture](./infrastructure/architecture-diagram.png)

## AWS Services
| Service | Purpose |
|---|---|
| S3 | Entry point + quarantine storage |
| Lambda | Serverless processing (with X-Ray tracing) |
| DynamoDB | Processing results storage |
| SNS | Real-time failure alerts |
| API Gateway | REST endpoint for the dashboard |
| CloudWatch | Custom metrics + alarms |
| **AWS SAM** | Infrastructure as Code — full stack deploys in one command |

## Deploy It Yourself
```bash
cd infrastructure
sam build
sam deploy --guided
```

## Live Demo
- Dashboard: [link]
- API endpoint: `GET {ApiUrl}/files`

## Engineering Decisions
- **IAM**: Uses SAM's built-in least-privilege policy templates (`S3ReadPolicy`, `DynamoDBCrudPolicy`, etc.) instead of broad managed policies
- **Observability**: X-Ray tracing enabled on all functions for distributed request tracing
- **CI/CD**: GitHub Actions deploys automatically on push via keyless OIDC federation (no long-lived AWS credentials in CI)

## Business Impact
- Zero idle cost — Lambda only runs during actual processing
- Bad data is automatically isolated, never corrupts the database
- Full stack redeployable from scratch in under 5 minutes
