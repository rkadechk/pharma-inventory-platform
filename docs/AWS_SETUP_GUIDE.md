# 🔧 AWS SETUP GUIDE - Day 1-2 (WEEK 1)

**Status:** This is what you need to complete FIRST before moving to Week 2
**Current Date:** February 2, 2026
**Timeline:** Day 1-2 (should take 4-8 hours)

---

## ❓ CAN YOU USE AWS FREE TIER?

### ✅ SHORT ANSWER: YES, BUT WITH LIMITS

**Good News:**
- AWS Free Tier gives you **12 months** of free services
- S3, Lambda, CloudWatch are **GENEROUS in free tier**
- You can complete this project for **MINIMAL cost** ($20-50 total)

**What You Can Use for FREE (12 months):**

| Service | Free Tier Allocation | Our Project Need | Cost |
|---------|---------------------|------------------|------|
| **S3** | 5 GB storage | 100 MB total | ✅ FREE |
| **Lambda** | 1 million requests/month | ~10,000 invocations | ✅ FREE |
| **CloudWatch** | 10 GB logs/month | ~1 GB logs | ✅ FREE |
| **Glue** | 1 million DPU-hours/month | ~10 DPU-hours | ✅ FREE |
| **Data Transfer** | 1 GB out/month | ~500 MB | ✅ FREE |

**What COSTS MONEY (but very cheap):**

| Service | Cost | Our Need | Monthly Cost |
|---------|------|----------|--------------|
| **RDS PostgreSQL** | $0.20/hour (micro) | 8 hours testing | **~$1.50** |
| **Redshift** | $1.26/hour (dc2.large) | 8 hours testing | **~$10** |
| **EC2** (optional) | $0.01/hour (t2.micro) | Development | **FREE** |

**Total Project Cost:** $10-50 (not $1000s) ✅

---

## 📋 PREREQUISITES BEFORE STARTING

Before you do anything, make sure you have:

- [ ] Valid email address (for AWS account)
- [ ] Valid credit card (AWS requires this, even for free tier)
- [ ] Phone number (for SMS verification)
- [ ] 30 minutes to set up account
- [ ] AWS CLI installed locally (optional but helpful)
- [ ] Python 3.10+ installed locally

---

## 🚀 STEP-BY-STEP: AWS ACCOUNT SETUP (1-2 hours)

### STEP 1: Create AWS Account (15 minutes)

**Go to:** https://aws.amazon.com/free/

```
1. Click "Create a FREE account"
2. Enter your email
3. Create password (strong: mix of upper, lower, numbers, symbols)
4. Account name: "pharma-project" or similar
5. Click "Verify Email" (check your inbox)
6. Click link in email verification
```

### STEP 2: Add Payment Method (10 minutes)

AWS requires a credit card (even for free tier). **Don't worry - you won't be charged unless you exceed free tier limits.**

```
1. After email verified, go to: https://console.aws.amazon.com/
2. Sign in with your email & password
3. AWS will prompt: "Add payment method"
4. Enter credit card info:
   ├─ Card number
   ├─ Expiration date
   ├─ CVV
   └─ Billing address
5. AWS charges $1 to verify (then refunds it within 1-5 business days)
```

### STEP 3: Choose Support Plan (5 minutes)

```
1. When asked about support plan, choose: "Basic" (FREE)
2. Click "Complete sign up"
3. You'll see: "Congratulations! You have successfully signed up for AWS"
```

### STEP 4: Enable Free Tier Notifications (5 minutes)

**IMPORTANT:** Set up alerts so you don't accidentally spend money

```
1. Go to: AWS Console → Billing → Preferences
2. Enable:
   ├─ "Receive Free Tier usage alerts"
   ├─ "Receive billing alerts"
   ├─ "Receive AWS Cost Anomaly Detection"
3. Enter email address for alerts
4. Click "Save preferences"
```

### STEP 5: Create IAM User (Optional but Recommended) (15 minutes)

**Why:** Don't use root account for day-to-day work. Create limited user instead.

```
1. Go to: AWS Console → IAM → Users
2. Click "Create user"
3. Name: "pharma-developer"
4. Check: "Access key - Programmatic access"
5. Next: Permissions
   ├─ Check "Attach existing policies directly"
   ├─ Search "S3FullAccess" → Check it
   ├─ Search "LambdaFullAccess" → Check it
   ├─ Search "GlueServiceRole" → Check it
   ├─ Search "RDSFullAccess" → Check it
   └─ Search "CloudWatchLogsFullAccess" → Check it
6. Next: Tags (skip)
7. Next: Review → Create user
8. ⚠️ SAVE THE CREDENTIALS (Access Key ID + Secret Access Key)
   └─ You'll need these for AWS CLI
```

---

## 🔐 SETUP SECURITY & PERMISSIONS

### Create IAM Role for Lambda & Glue

**Go to:** AWS Console → IAM → Roles

```
Step 1: Create Role for Lambda
├─ Click "Create role"
├─ Service: "Lambda"
├─ Click Next
├─ Add permissions:
│  ├─ AmazonS3FullAccess
│  ├─ CloudWatchLogsFullAccess
│  └─ AWSLambdaBasicExecutionRole
├─ Role name: "pharma-lambda-role"
└─ Create role

Step 2: Create Role for Glue
├─ Click "Create role"
├─ Service: "Glue"
├─ Click Next
├─ Add permissions:
│  ├─ AWSGlueServiceRole
│  ├─ AmazonS3FullAccess
│  └─ CloudWatchLogsFullAccess
├─ Role name: "pharma-glue-role"
└─ Create role
```

### Create Security Group for Database

**Go to:** AWS Console → EC2 → Security Groups

```
Step 1: Create Security Group
├─ Click "Create security group"
├─ Name: "pharma-database-sg"
├─ VPC: Default VPC
└─ Description: "Allows access to pharma database"

Step 2: Add Inbound Rules
├─ Rule 1:
│  ├─ Type: PostgreSQL
│  ├─ Protocol: TCP
│  ├─ Port: 5432
│  ├─ Source: 0.0.0.0/0 (allows your IP)
│  └─ Description: "PostgreSQL access"
└─ Create security group
```

---

## 📦 SETUP S3 BUCKETS (15 minutes)

**Go to:** AWS Console → S3

### Create Bucket 1: Raw Data

```
1. Click "Create bucket"
2. Bucket name: "pharma-raw-data-YOUR-INITIALS"
   └─ Must be GLOBALLY unique (add date/initials)
3. Region: us-east-1 (cheapest)
4. Object Ownership: ACLs disabled
5. Block all Public Access: ✅ CHECKED
6. Enable versioning: ✅ CHECKED
7. Enable encryption: ✅ CHECKED (SSE-S3)
8. Click "Create bucket"

9. After creation, create folders inside:
   ├─ Click bucket name
   ├─ Click "Create folder"
   ├─ Name: "facilities" → Create
   ├─ Name: "medications" → Create
   ├─ Name: "inventory" → Create
   ├─ Name: "consumption" → Create
   ├─ Name: "transfers" → Create
   ├─ Name: "external_signals" → Create
   ├─ Name: "demand_forecast" → Create
   └─ Name: "replenishment_orders" → Create
```

### Create Bucket 2: Curated Data

```
1. Click "Create bucket"
2. Bucket name: "pharma-curated-data-YOUR-INITIALS"
3. Region: us-east-1
4. Same settings as above (versioning, encryption, etc.)
5. Click "Create bucket"

6. Create folders:
   ├─ "cleaned" → Create
   ├─ "enriched" → Create
   └─ "aggregated" → Create
```

### Create Bucket 3: Logs

```
1. Click "Create bucket"
2. Bucket name: "pharma-logs-YOUR-INITIALS"
3. Region: us-east-1
4. Create folder: "glue-logs"
5. Create folder: "lambda-logs"
```

### Set Up Lifecycle Policies

**For pharma-raw-data bucket:**

```
1. Click bucket name
2. Go to "Management" tab
3. Click "Create lifecycle rule"
4. Rule name: "archive-raw-data"
5. Rule scope: Apply to all objects
6. Lifecycle rule actions:
   ├─ Check "Move current versions..."
   ├─ Days: 90
   ├─ Storage class: GLACIER
   └─ Create rule
```

---

## 🔌 INSTALL & CONFIGURE AWS CLI (20 minutes)

**Why:** Makes S3 uploads, Lambda testing, etc. much easier

### Step 1: Install AWS CLI

**On Windows (CMD):**
```cmd
# Using pip
pip install awscli

# Or download: https://awscli.amazonaws.com/AWSCLIV2.msi
# Then install the MSI file
```

**Verify installation:**
```cmd
aws --version
```

### Step 2: Configure AWS CLI

```cmd
aws configure
```

This will prompt:
```
AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-east-1
Default output format [None]: json
```

**Where to get these:**
1. Go to: AWS Console → IAM → Users
2. Click your user name
3. Go to "Security credentials" tab
4. Under "Access keys", click "Create access key"
5. Copy the **Access Key ID** and **Secret Access Key**

### Step 3: Test AWS CLI

```cmd
# List your S3 buckets
aws s3 ls

# Should output:
# 2025-02-02 15:30:45 pharma-curated-data-rk
# 2025-02-02 15:30:30 pharma-logs-rk
# 2025-02-02 15:30:15 pharma-raw-data-rk
```

✅ If you see your buckets, AWS CLI is configured correctly!

---

## 🛠️ SETUP LOCAL DEVELOPMENT ENVIRONMENT (30 minutes)

### Step 1: Create Project Directory

```cmd
# Navigate to your project
cd c:\Users\kadec\Documents\Interview\ prep\Capstone\ Project\pharma-inventory-platform

# Create directories
mkdir lambda-functions
mkdir glue-jobs
mkdir terraform
mkdir scripts
```

### Step 2: Create Python Virtual Environment

```cmd
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate

# You should see: (venv) C:\path\to\project>
```

### Step 3: Install Python Dependencies

```cmd
# Create requirements.txt
echo boto3==1.28.0 > requirements.txt
echo pandas==2.0.0 >> requirements.txt
echo pyspark==3.4.0 >> requirements.txt
echo psycopg2-binary==2.9.0 >> requirements.txt
echo python-dotenv==1.0.0 >> requirements.txt

# Install
pip install -r requirements.txt
```

### Step 4: Create Environment File

**Create file:** `.env`

```
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# S3 Buckets
RAW_DATA_BUCKET=pharma-raw-data-YOUR-INITIALS
CURATED_DATA_BUCKET=pharma-curated-data-YOUR-INITIALS
LOGS_BUCKET=pharma-logs-YOUR-INITIALS

# Database (fill in after you create it)
DB_HOST=your-db-endpoint
DB_PORT=5432
DB_NAME=pharma_db
DB_USER=admin
DB_PASSWORD=YourSecurePassword123!
```

⚠️ **Don't commit .env to Git!** Add to `.gitignore`

---

## 🗄️ CREATE DATABASE INSTANCE (30 minutes)

### Option A: RDS PostgreSQL (Recommended for Learning)

**Go to:** AWS Console → RDS → Create database

```
1. Choose database creation method: "Standard create"
2. Engine: "PostgreSQL"
3. Version: PostgreSQL 14.7
4. Templates: "Free tier"
5. DB instance identifier: "pharma-db"
6. Master username: "admin"
7. Master password: "YourSecurePassword123!" (strong password)
8. DB instance class: db.t3.micro (FREE tier)
9. Storage: General Purpose (gp2), 20 GB
10. Enhanced monitoring: Disabled
11. Backup retention: 7 days
12. Encryption: Enabled
13. Click "Create database"
```

**Wait 5-10 minutes for creation...**

After creation:
```
1. Click your DB instance
2. Copy "Endpoint" (looks like: pharma-db.xxxxx.us-east-1.rds.amazonaws.com)
3. Note the port: 5432
4. Add to your .env file
```

### Option B: Redshift (More Powerful, But Not Free)

**⚠️ Costs $1.26/hour** - Only use for testing, shut down when not in use

```
1. AWS Console → Redshift → Create cluster
2. Cluster name: "pharma-redshift"
3. Node type: dc2.large
4. Number of nodes: 1
5. Master username: admin
6. Master password: YourSecurePassword123!
7. Database name: pharma_db
8. Click "Create cluster"
```

**Wait 10-15 minutes...**

---

## ✅ SETUP CHECKLIST - END OF DAY 2

Complete this checklist to confirm you're ready for Week 2:

### Account & Security
- [ ] AWS account created
- [ ] Credit card added
- [ ] Billing alerts enabled
- [ ] IAM user created (pharma-developer)
- [ ] Access keys saved securely
- [ ] IAM roles created (Lambda, Glue)
- [ ] Security groups created

### S3 Buckets
- [ ] pharma-raw-data bucket created
- [ ] pharma-curated-data bucket created
- [ ] pharma-logs bucket created
- [ ] Folder structure created
- [ ] Encryption enabled
- [ ] Versioning enabled
- [ ] Lifecycle policies set

### AWS CLI
- [ ] AWS CLI installed
- [ ] AWS CLI configured
- [ ] `aws s3 ls` command works
- [ ] Access keys stored securely

### Local Environment
- [ ] Project directory created
- [ ] Python venv created & activated
- [ ] Dependencies installed
- [ ] .env file created (with placeholder values)
- [ ] .gitignore updated

### Database
- [ ] RDS PostgreSQL instance created (or Redshift)
- [ ] Database endpoint noted
- [ ] Master username/password set
- [ ] Security group configured
- [ ] Can connect from your computer

### Cost Monitoring
- [ ] Billing alerts set to $10
- [ ] Cost Anomaly Detection enabled
- [ ] AWS Cost Explorer bookmarked
- [ ] Commitment to shut down unused resources

---

## 💰 COST BREAKDOWN - What You'll Actually Pay

### During Development (Weeks 1-2):

| Service | Usage | Cost |
|---------|-------|------|
| S3 | 100 MB stored | $0.01 |
| Lambda | 10,000 invocations | FREE |
| CloudWatch | 1 GB logs | FREE |
| RDS PostgreSQL | 8 hours | $1.50 |
| Data Transfer | 500 MB | FREE |
| **Total Week 2** | | **~$1.50** |

### During Feature Development (Weeks 3-12):

| Service | Usage | Cost |
|---------|-------|------|
| S3 | 500 MB stored | $0.05 |
| Lambda | 100,000 invocations | FREE |
| CloudWatch | 5 GB logs | FREE |
| Glue | 20 DPU-hours | FREE (some free) |
| RDS PostgreSQL | 40 hours | $8 |
| **Total per week** | | **~$8** |

### Total Project Cost (12 weeks):
- **Weeks 1-2:** $3
- **Weeks 3-12:** ~$80
- **TOTAL:** ~$83 (plus $1 verification fee, refunded)

**This is EXTREMELY cheap compared to:**
- Cloud development: Usually $1000+/month
- On-premises infrastructure: $10,000+
- Other cloud providers: Similar costs

---

## ⚠️ HOW TO AVOID UNEXPECTED CHARGES

### Turn Off Expensive Services When Not Using:

```cmd
# Stop RDS instance (saves ~$0.20/hour)
aws rds stop-db-instance --db-instance-identifier pharma-db

# Stop Redshift cluster (if you created it)
aws redshift pause-cluster --cluster-identifier pharma-redshift
```

### Set Up Cost Alarms:

```
1. AWS Console → CloudWatch → Alarms
2. Click "Create alarm"
3. Metric: AWS Billing
4. Statistic: Maximum
5. Threshold: $10
6. Action: Send email
7. Create alarm
```

### Monitor Costs Weekly:

```
1. AWS Console → Billing → Cost Explorer
2. Filter by service
3. Look for unusual spikes
4. Stop services you're not using
```

---

## 🆘 TROUBLESHOOTING DAY 1-2 SETUP

### "I can't create an S3 bucket - bucket name already exists"
→ Add random numbers or date to bucket name
→ Example: `pharma-raw-data-20250202-abc`

### "AWS CLI configure isn't working"
→ Check you copied the correct Access Key ID
→ Check there are no extra spaces
→ Try: `aws configure --profile pharma`

### "I can't connect to RDS database"
→ Check security group allows inbound on port 5432
→ Check your IP is whitelisted (use 0.0.0.0/0 for now)
→ Check database has "Public accessibility" = true

### "Free tier services say they cost money"
→ Check if you selected the right instance size
→ Check if you went over free tier limits
→ Check region (us-east-1 is cheapest)

### "I'm worried about accidental charges"
→ Stop RDS when not in use
→ Set billing alert to $5
→ Monitor AWS Cost Explorer weekly
→ Delete data regularly to save S3 space

---

## 🎓 WHAT YOU'LL HAVE AFTER DAY 1-2

```
Your AWS Infrastructure (After Day 1-2)
════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────┐
│                    AWS ACCOUNT                           │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   IAM User  │  │ Billing     │  │  CloudWatch │      │
│  │ pharma-dev  │  │ Alerts      │  │  Alarms     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          STORAGE (S3 Buckets)                    │   │
│  │  ├─ pharma-raw-data/                             │   │
│  │  │  ├─ facilities/                               │   │
│  │  │  ├─ medications/                              │   │
│  │  │  ├─ inventory/                                │   │
│  │  │  └─ ... (8 folders total)                     │   │
│  │  ├─ pharma-curated-data/                         │   │
│  │  │  ├─ cleaned/                                  │   │
│  │  │  ├─ enriched/                                 │   │
│  │  │  └─ aggregated/                               │   │
│  │  └─ pharma-logs/                                 │   │
│  │     ├─ glue-logs/                                │   │
│  │     └─ lambda-logs/                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │        DATABASE (RDS PostgreSQL)                 │   │
│  │                                                  │   │
│  │  Endpoint: pharma-db.xxxxx.us-east-1.rds...    │   │
│  │  Port: 5432                                      │   │
│  │  Master user: admin                              │   │
│  │  Status: Ready for data                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │        IAM ROLES & SECURITY GROUPS              │   │
│  │                                                  │   │
│  │  ✓ pharma-lambda-role (for Lambda)               │   │
│  │  ✓ pharma-glue-role (for Glue)                   │   │
│  │  ✓ pharma-database-sg (for database access)      │   │
│  │  ✓ Encryption enabled                            │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

---

## 📝 NEXT STEPS (Week 2)

Once you complete this Day 1-2 setup, you're ready for:

**Week 2, Day 1:** Upload your synthetic data to S3
**Week 2, Day 2:** Create Lambda validator function
**Week 2, Day 3-4:** Create Glue job for data cleaning
**Week 2, Day 5:** Load data into database

---

## ✅ READY FOR WEEK 2?

Before you move on, verify:

- [ ] AWS account fully set up
- [ ] All buckets created with correct structure
- [ ] IAM user & roles created
- [ ] RDS database running
- [ ] AWS CLI working on your computer
- [ ] .env file with all credentials
- [ ] Billing alerts set
- [ ] Budget: Understanding it's only ~$5-10

**You're ready! Move to Week 2 Day 1 🚀**

---

## 📞 SUPPORT RESOURCES

### AWS Learning Resources:
- **AWS Free Tier Guide:** https://aws.amazon.com/free/
- **AWS S3 Documentation:** https://docs.aws.amazon.com/s3/
- **AWS IAM Guide:** https://docs.aws.amazon.com/iam/
- **AWS RDS PostgreSQL:** https://docs.aws.amazon.com/rds/

### Troubleshooting:
- AWS Support: https://console.aws.amazon.com/support/
- AWS Forums: https://forums.aws.amazon.com/
- Stack Overflow: Tag with `amazon-aws`

### Helpful Tools:
- **AWS Console:** https://console.aws.amazon.com/
- **AWS CLI Documentation:** https://docs.aws.amazon.com/cli/
- **IAM Best Practices:** https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

