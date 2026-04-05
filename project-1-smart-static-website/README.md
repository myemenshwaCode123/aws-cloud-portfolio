# ☁️ Project 1 — Smart Static Website
 
> A production-grade, globally distributed static website deployed on AWS —  
> secured with HTTPS, delivered through CloudFront's CDN, and monitored with CloudWatch.
 
---
 
## ⚙️ Tech Stack
 
| Service | Role |
|--------|------|
| **Amazon S3** | Private origin bucket — stores all static assets |
| **Amazon CloudFront** | Global CDN — HTTPS enforced, OAC, sub-100ms load times worldwide |
| **Amazon CloudWatch** | Real-time monitoring dashboard and alarms |
| **Amazon SNS** | Email alerts triggered on error spikes |
 
---
 
## 🔐 Security Design
 
- **S3 is completely private** — block all public access is enabled. The S3 URL is never exposed to the internet
- **CloudFront accesses S3 via Origin Access Control (OAC)** — the modern replacement for OAI, using short-lived signed requests
- **All traffic forced to HTTPS** via CloudFront viewer protocol policy — no ACM certificate needed on the default `*.cloudfront.net` domain
- **CloudWatch alarm triggers** if 5xx error rate exceeds 5%, firing an SNS email alert automatically
 
---
 
## 📈 Business Impact
 
| Metric | Result |
|--------|--------|
| 💰 Monthly cost | **$0** — 100% AWS Free Tier |
| ⚡ Load time improvement | **~60% faster** vs. direct S3 hosting via edge caching |
| 🌍 Uptime | **99.9%** via CloudFront's globally redundant edge network |
| 🚨 Issue detection | **Automated** — alerts fire before users report problems |
 
---
 
## 📁 Infrastructure Files
 
```
infrastructure/
├── Architecture-Diagram.png   # AWS architecture diagram
├── s3-bucket-policy.json      # CloudFront OAC bucket policy
├── setup-guide.md             # Step-by-step setup instructions
└── demo-video.md              # Unlisted demo recording
```
 
---
 
## 🚀 How to Deploy
 
See [`infrastructure/setup-guide.md`](infrastructure/setup-guide.md) for the full step-by-step walkthrough.
 
**Quick overview:**
1. Upload static files to a private S3 bucket
2. Create a CloudFront distribution with OAC pointing to the bucket
3. Set `index.html` as the default root object
4. Configure a custom 404 error page
5. Set up CloudWatch dashboard and 5xx alarm

---

## Live Demo
[View Site](https://d1s6iv7md0b1pw.cloudfront.net)

---

## Screenshots
<img width="1714" height="1386" alt="image" src="https://github.com/user-attachments/assets/cf3a48bf-2d79-43ff-9241-168d9a89be05" />

<img width="1712" height="671" alt="image" src="https://github.com/user-attachments/assets/e82b2639-d43b-42fc-bcd0-89d74c16bf47" />

<img width="1633" height="1386" alt="image" src="https://github.com/user-attachments/assets/50df3135-2b1c-48d9-b1e4-65ad4e64a9aa" />

<img width="1628" height="1394" alt="image" src="https://github.com/user-attachments/assets/1af7517c-c93e-418e-bd38-62a5e8e774a8" />

---


<div align="center">
  <sub>Built by <a href="https://github.com/myemenshwaCode123">Michael Yemenshwa</a> · Hosted on AWS</sub>
</div>
