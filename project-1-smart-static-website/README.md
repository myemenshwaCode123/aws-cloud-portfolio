# Project 1: Smart Static Website

## Overview
A production-grade static website deployed on AWS with global CDN delivery, HTTPS enforcement,
and real-time monitoring — not just a basic S3 upload.

## Architecture

User → CloudFront (CDN + HTTPS) → S3 (Private Origin)
↓
ACM (SSL Certificate)
↓
CloudWatch (Dashboards + Alarms) → SNS (Email Alerts)

## AWS Services Used
| Service | Purpose |
|---------|---------|
| S3 | Secure private storage for site files |
| CloudFront | Global CDN — sub-100ms load times worldwide |
| ACM | Free SSL/TLS certificate (HTTPS) |
| CloudWatch | Real-time monitoring dashboard + alarms |
| SNS | Email alerts on error spikes |

## Security Design
- S3 bucket is **completely private** — no public access
- CloudFront accesses S3 via **Origin Access Control (OAC)** — modern replacement for OAI
- All traffic forced to HTTPS via viewer protocol policy
- CloudWatch alarm triggers if 5xx error rate exceeds 5%

## Business Impact
- **99.9% uptime** via CloudFront's globally redundant edge network
- **~60% faster** load times vs. direct S3 hosting (edge caching)
- **$0/month** hosting cost on AWS Free Tier
- Automated alerting means issues are caught before users report them

## Live Demo
[View Site](https://d1s6iv7md0b1pw.cloudfront.net)

## Screenshots
*(Add screenshots of your site, CloudWatch dashboard, and CloudFront distribution here)*

<img width="1706" height="1338" alt="image" src="https://github.com/user-attachments/assets/e2370d13-ca69-45f5-82c3-5eb3d8a14680" />

<img width="1633" height="1386" alt="image" src="https://github.com/user-attachments/assets/50df3135-2b1c-48d9-b1e4-65ad4e64a9aa" />

<img width="1628" height="1394" alt="image" src="https://github.com/user-attachments/assets/1af7517c-c93e-418e-bd38-62a5e8e774a8" />
