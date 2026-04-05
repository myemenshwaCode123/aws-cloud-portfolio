# Project 1: Smart Static Website — Setup Guide
 
> **Stack:** S3 · CloudFront · CloudWatch  
> **Cost:** 100% AWS Free Tier  
> **Region:** `us-east-1` for all services  
> **Domain:** Default `*.cloudfront.net` — no custom domain, no ACM required
 
---
 
## Prerequisites
 
- An AWS account with console access
- (Optional) A custom domain managed via Route 53, Namecheap, or similar DNS registrar
 
---
 
## Step 1 — Build & prepare static files
 
Create the following two files in `project-1-smart-static-website/src/`:
 
| File | Purpose |
|------|---------|
| `index.html` | Main portfolio page |
| `error.html` | Custom 404 error page |
 
---
 
## Step 2 — Create the S3 bucket
 
1. Go to **AWS Console → S3 → Create bucket**
2. Set **Bucket name**: `my-portfolio-site-<YOUR_INITIALS>-2025` *(must be globally unique)*
3. Set **Region**: `us-east-1`
4. Keep **Block ALL public access**: ✅ **ENABLED** — CloudFront accesses the bucket privately via OAC
5. Click **Create bucket**
6. Open the bucket → **Upload** → drag in `index.html` and `error.html`
 
---
 
## Step 3 — SSL/TLS certificate (ACM)
 
> ✅ **Skipped — not needed for this setup.**
 
This project uses the default CloudFront domain (`*.cloudfront.net`), which comes with HTTPS automatically included — no ACM certificate is required. CloudFront handles the SSL/TLS termination on its own.
 
ACM is only needed if you attach a **custom domain** (e.g. `myportfolio.com`). If you do that in the future, the certificate must be requested in `us-east-1` regardless of where your S3 bucket lives.
 
---
 
## Step 4 — Create the CloudFront distribution
 
1. Go to **AWS Console → CloudFront → Create distribution**
2. Configure as follows:
 
| Setting | Value |
|---------|-------|
| Origin domain | Select your S3 bucket |
| Origin access | **Origin access control (OAC)** → Create new OAC (`portfolio-oac`) |
| Viewer protocol policy | **Redirect HTTP to HTTPS** |
| Cache policy | `CachingOptimized` (AWS managed) |
| Price class | Use only North America and Europe |
| Alternate domain (CNAME) | Leave blank |
| Custom SSL certificate | Leave blank — CloudFront uses default `*.cloudfront.net` HTTPS |
| Default root object | `index.html` |
 
3. Click **Create distribution**
 
### Apply the S3 bucket policy
 
After creation, AWS will prompt you to copy a bucket policy. Apply it:
 
1. Go to your **S3 bucket → Permissions → Bucket policy → Edit**
2. Paste the policy from `s3-bucket-policy.json` in this folder
3. Replace the three placeholder values:
   - `YOUR_BUCKET_NAME` → your actual bucket name
   - `YOUR_ACCOUNT_ID` → your 12-digit AWS account ID
   - `YOUR_DISTRIBUTION_ID` → the CloudFront distribution ID (e.g. `E1ABCDEF123456`)
4. **Save changes**
 
---
 
## Step 5 — Configure custom error pages
 
1. In your CloudFront distribution → **Error pages** tab
2. Click **Create custom error response**:
 
| Setting | Value |
|---------|-------|
| HTTP error code | `404` |
| Response page path | `/error.html` |
| HTTP response code | `404` |
 
3. Save
 
---
 
## Step 6 — Set up CloudWatch monitoring
 
### Create a dashboard
 
1. Go to **CloudWatch → Dashboards → Create dashboard**
2. Name it `Portfolio-Website-Dashboard`
3. Add a **Line widget** with these CloudFront metrics:
   - `Requests`
   - `BytesDownloaded`
   - `4xxErrorRate`
   - `5xxErrorRate`
4. Add a **Number widget** with the same metrics for at-a-glance readout
5. Save dashboard
 
### Create an alarm
 
1. **CloudWatch → Alarms → Create alarm**
2. Select metric: **CloudFront → 5xxErrorRate** for your distribution
3. Threshold: Greater than `5` (5% error rate)
4. Create new **SNS topic**: `portfolio-alerts` → enter your email
5. Confirm the email subscription
6. Alarm name: `Portfolio-High-Error-Rate`
 
---
 
## Step 7 — Test
 
1. Copy your **CloudFront Distribution domain name** (e.g. `d1234abcd.cloudfront.net`)
2. Open it in a browser — you should see your site over HTTPS ✅
3. Append a non-existent path (e.g. `/fakeurl`) to verify the custom 404 page loads ✅
 
---
 
## Architecture summary
 
```
Internet User (HTTPS)
        │
        ▼
Amazon CloudFront ──────────────► CloudWatch (Dashboards & Alarms)
CDN · HTTPS · OAC                 5xxErrorRate · SNS alerts
*.cloudfront.net
        │ (OAC — private)
        ▼
    Amazon S3
  (Private bucket)
```
 
- **S3** never exposes a public endpoint — CloudFront reads it via Origin Access Control
- **CloudFront** provides HTTPS automatically on the default `*.cloudfront.net` domain — no ACM certificate needed
- **CloudWatch** monitors error rates and sends SNS alerts when thresholds are crossed
