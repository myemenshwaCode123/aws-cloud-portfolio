# ☁️ AWS Cloud Portfolio

A collection of production-grade AWS projects demonstrating serverless architecture, Infrastructure as Code, GenAI/RAG integration, and DevOps automation — built end-to-end on AWS Free Tier.

## Projects

| # | Project | Services Used | Highlights |
|---|---------|--------------|------------|
| 1 | [Smart Static Website](./project-1-smart-static-website) | S3, CloudFront, ACM, CloudWatch | Global CDN, HTTPS via Origin Access Control, zero public S3 access |
| 2 | [Silent Scalper — Serverless Pipeline](./project-2-silent-scalper) | S3, Lambda, DynamoDB, SNS, API Gateway | Event-driven pipeline, live monitoring dashboard, X-Ray tracing |
| 3 | [Smart Vault — Automated Backups](./project-3-smart-vault) | EC2, EBS, Lambda, EventBridge, SNS | Cross-region disaster recovery, keyless SSM instance access |
| 4 | [AI Customer Service Bot](./project-4-ai-customer-bot) | API Gateway, Lambda, DynamoDB, Bedrock | Retrieval-Augmented Generation, cross-region inference profile |

## Engineering Practices Demonstrated

- **Infrastructure as Code** — Projects 2–4 deploy their entire stack via AWS SAM in one command; zero manual console configuration for compute, data, or networking resources
- **CI/CD** — GitHub Actions auto-deploys on push using keyless OIDC federation (no static AWS credentials stored in CI)
- **Least-privilege IAM** — scoped SAM policy templates and custom resource-level policies throughout, not broad managed permissions
- **Observability** — CloudWatch custom metrics, alarms, and X-Ray distributed tracing on every project
- **Security-first design** — private S3 buckets behind CloudFront OAC, SSM Session Manager instead of SSH, encrypted data in transit, no long-lived credentials anywhere in the pipeline
- **Real production debugging, not just a happy path** — Project 4's README documents an actual mid-build AWS Bedrock model lifecycle migration (a legacy model deprecation, then a cross-region inference profile requirement) and an LLM instruction-following bug found and fixed post-deploy

## Skills Demonstrated

`AWS` `Serverless` `AWS SAM` `Infrastructure as Code` `CI/CD` `GitHub Actions` `OIDC` `Lambda` `S3` `DynamoDB` `CloudFront` `API Gateway` `Amazon Bedrock` `GenAI` `RAG` `EventBridge` `SNS` `CloudWatch` `X-Ray` `EC2` `EBS` `IAM` `Python`

## Repo Structure

```
aws-cloud-portfolio/
├── project-1-smart-static-website/
│   ├── src/                    # Static site (HTML/CSS)
│   ├── infrastructure/         # IAM policy, setup docs
│   ├── screenshots/
│   └── README.md
├── project-2-silent-scalper/
│   ├── lambda/                 # processor.py, query.py
│   ├── infrastructure/         # SAM template.yaml
│   ├── dashboard/               # Live monitoring frontend
│   ├── screenshots/
│   └── README.md
├── project-3-smart-vault/
│   ├── lambda/                 # backup_manager.py (cross-region DR)
│   ├── infrastructure/         # SAM template.yaml
│   ├── screenshots/
│   └── README.md
├── project-4-ai-customer-bot/
│   ├── lambda/                 # chatbot.py (RAG-enabled)
│   ├── scripts/                 # build_knowledge_base.py
│   ├── infrastructure/         # SAM template.yaml
│   ├── screenshots/
│   └── README.md
├── .github/workflows/          # CI/CD pipeline, one per project
├── LICENSE
└── README.md                   # you are here
```

## Note on Live Deployments

Live AWS resources were deployed and tested during an AWS Free Tier trial period. Some live demo links may no longer be active after the trial concluded — all infrastructure is fully defined as code in each project's `infrastructure/` folder and reproducible with `sam deploy`. Screenshots and test output proving each system worked in production are included in every project's `screenshots/` folder.

## Connect

Questions about any of these projects, or want to talk about a role? Reach out:

- LinkedIn: www.linkedin.com/in/m-yemenshwa
- Email: michaelyemenshwa@gmail.com
- GitHub: [@myemenshwaCode123](https://github.com/myemenshwaCode123)
