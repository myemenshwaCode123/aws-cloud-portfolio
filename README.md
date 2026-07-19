# ☁️ AWS Cloud Portfolio

A collection of production-grade AWS projects demonstrating serverless architecture, Infrastructure as Code, GenAI/RAG integration, and DevOps automation — built end-to-end on AWS Free Tier.

## Projects

| # | Project | Services Used | Difficulty |
|---|---------|--------------|------------|
| 1 | [Smart Static Website](./project-1-smart-static-website) | S3, CloudFront, ACM, CloudWatch | Beginner |
| 2 | [Silent Scalper — Serverless Pipeline](./project-2-silent-scalper) | S3, Lambda, DynamoDB, SNS, API Gateway | Intermediate |
| 3 | [Smart Vault — Automated Backups](./project-3-smart-vault) | EC2, EBS, Lambda, EventBridge, SNS | Intermediate |
| 4 | [AI Customer Service Bot](./project-4-ai-customer-bot) | API Gateway, Lambda, DynamoDB, Bedrock | Advanced |

## Architecture Highlights
- All projects follow AWS Well-Architected Framework principles
- Infrastructure-as-Code where applicable
- Security-first design (IAM least privilege, encryption at rest/transit)
- CloudWatch monitoring and SNS alerting on every project

## Engineering Practices Demonstrated
- **Infrastructure as Code** — Projects 2–4 deploy via AWS SAM in one command; zero manual console configuration for compute/data resources
- **CI/CD** — GitHub Actions auto-deploys on push using keyless OIDC federation (no static AWS credentials in CI)
- **Least-privilege IAM** — scoped SAM policy templates and custom resource-level policies throughout, not broad managed permissions
- **Observability** — CloudWatch custom metrics, alarms, and X-Ray distributed tracing on every project
- **Security-first design** — private S3 buckets behind CloudFront OAC, SSM Session Manager instead of SSH, encrypted data in transit
- **Real production debugging** — Project 4's README documents an actual mid-build AWS Bedrock model lifecycle migration, not just a happy-path tutorial


## Skills Demonstrated
`AWS` `Serverless` `Lambda` `S3` `DynamoDB` `CloudFront` `API Gateway` `Amazon Bedrock` `GenAI` `EventBridge` `SNS` `CloudWatch` `EC2` `EBS` `IAM`

## Note on Live Deployments
Live AWS resources were deployed and tested during an AWS Free Tier trial period. Some live
demo links may no longer be active after the trial concluded — all infrastructure is fully
defined as code in each project's `infrastructure/` folder and reproducible with `sam deploy`.
Screenshots and test output proving each system worked in production are included in every
project's `screenshots/` folder.
