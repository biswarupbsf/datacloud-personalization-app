# 🎯 Master Data Ingestion Path - Complete Guide
## Ingest All Data Objects into Salesforce Data Cloud Org

---

## 📊 Overview of Data Objects Created

### **Total Data Objects: 2**

| # | Object Name | File Location | Records | Size | Description |
|---|-------------|---------------|---------|------|-------------|
| 1 | **Individual Engagement** | `data/synthetic_engagement.csv` | 100 | 54 KB | Omnichannel engagement metrics |
| 2 | **Individual Insights** | `data/individual_insights.csv` | 529 | 129 KB | Time-series behavioral insights |

**Total Records:** 629  
**Total Size:** 183 KB

---

## 📋 Data Object Details

### **1. Individual Engagement (`synthetic_engagement.csv`)**

**Purpose:** Master individual records with omnichannel engagement data

**Schema (31 fields):**
```
id                       → Primary Key (Salesforce Individual ID)
FirstName                → Text
LastName                 → Text
Name                     → Text (Full Name)
Email                    → Email (Real addresses)
Phone                    → Phone (Indian format: +91xxxxxxxxxx)
Phone_Display            → Text (Display format)

Email Engagement:
├─ email_opens           → Number
├─ email_clicks          → Number
├─ email_bounces         → Number
├─ email_unsubscribes    → Number
├─ email_campaigns_received → Number
└─ email_campaigns_engaged  → List (JSON)

SMS Engagement:
├─ sms_sends             → Number
├─ sms_opens             → Number
├─ sms_clicks            → Number
├─ sms_optouts           → Number
└─ sms_open_rate         → Number (Percent)

WhatsApp Engagement:
├─ whatsapp_sends        → Number
├─ whatsapp_reads        → Number
├─ whatsapp_replies      → Number
├─ whatsapp_optouts      → Number
└─ whatsapp_read_rate    → Number (Percent)

Push Notification:
├─ push_sends            → Number
├─ push_opens            → Number
├─ push_clicks           → Number
└─ push_open_rate        → Number (Percent)

Website Engagement:
├─ website_product_views → Number
├─ website_add_to_cart   → Number
├─ website_cart_abandons → Number
├─ website_purchases     → Number
├─ products_browsed      → List (JSON)
├─ products_purchased    → List (JSON)
└─ total_order_value     → Currency

Scoring:
├─ engagement_score      → Number (0-10)
├─ omnichannel_score     → Number (0-10, weighted)
├─ preferred_channel     → Text (Email|SMS|WhatsApp|Push|Website)
├─ favorite_category     → Text
├─ last_engagement_date  → DateTime
└─ data_source           → Text ('synthetic_omnichannel')
```

**Sample Data:**
- Biswarup Banerjee (bbanerjee@salesforce.com) - Score: 6.88
- Ashish Desai - Score: 6.73
- Deepika Chauhan - Score: 6.65
- Total: 100 individuals with real Indian names

---

### **2. Individual Insights (`individual_insights.csv`)**

**Purpose:** Time-series behavioral insights tracking sentiment, lifestyle, and purchase intent over 90 days

**Schema (17 fields):**
```
Primary Keys (Composite):
├─ Individual_Id         → Text (Foreign Key to Engagement.id)
└─ Event_Timestamp       → DateTime (ISO 8601 format)

Individual Info:
├─ Individual_Name       → Text
├─ Individual_FirstName  → Text
├─ Individual_LastName   → Text
├─ Individual_Email      → Email
└─ Individual_Phone      → Phone

Behavioral Insights:
├─ Current_Sentiment     → Text (Happy|Elated|Anxious|Frustrated|Sad|Angry|Disgusted|Calm|etc.)
├─ Lifestyle_Quotient    → Text (Luxury Seeker|Adventurer|Homebody|Foodie|Careerist|etc.)
├─ Health_Profile        → Text (Athletic|Healthy|Fit|Stressed|Hypertensive|Sedentary|etc.)
├─ Fitness_Milestone     → Text (Rookie|Beginner|Amateur|Intermediate|Advanced|Professional|Elite|Champion)
├─ Purchase_Intent       → Text (Very High|Immediate|High|Considering|Medium|Tepid|Low|Not Interested)
├─ Favourite_Brand       → Text (Samsung|Apple|Nike|Amazon|Netflix|Tesla|etc.)
├─ Favourite_Destination → Text (Maldives|Singapore|Dubai|Switzerland|Amsterdam|etc.)
├─ Hobby                 → Text (Reading|Hiking|Gaming|Photography|Yoga|etc.)
├─ Imminent_Event        → Text (Free-form event description)
└─ data_source           → Text ('synthetic_insights')
```

**Sample Data:**
- 529 insight snapshots
- 100 unique individuals (5-6 snapshots each)
- Time range: Last 90 days
- Biswarup Banerjee has 6 insight records

---

## 🚀 INGESTION PATH (Choose One)

---

## **PATH 1: UI-Based Upload (Easiest - 5 Minutes)** ⭐ RECOMMENDED

Perfect for: One-time uploads, manual data loading, quick testing

### **Prerequisites:**
- ✅ Access to Salesforce Data Cloud org
- ✅ CSV files available locally
- ✅ 5 minutes of time

### **Step-by-Step:**

#### **STEP 1: Login to Data Cloud (30 seconds)**

1. Go to: https://login.salesforce.com
2. Login with your SFtutor org credentials
3. Click **App Launcher** (grid icon)
4. Search and open **"Data Cloud"**

#### **STEP 2: Upload Individual Engagement Data (2 minutes)**

1. **Navigate:**
   - Click **Data Streams** tab
   - Click **"New"** or **"New Data Stream"**

2. **Select Source:**
   - Choose **"Upload"** or **"CSV Upload"**
   - Click **Next**

3. **Upload File:**
   - Click **"Choose File"** or **"Browse"**
   - Navigate to: `/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/`
   - Select: **`synthetic_engagement.csv`**
   - Click **"Upload"**

4. **Configure Stream:**
   - **Stream Name:** `Individual_Engagement_Stream`
   - **Data Lake Object Name:** `Individual_Engagement`
   - **Description:** "Omnichannel engagement metrics for 100 individuals"
   - Click **Next**

5. **Set Primary Key:**
   - **Primary Key Field:** `id`
   - **Data Type:** Text
   - ✅ Check "This is a unique identifier"
   - Click **Next**

6. **Map Fields** (Auto-detected, verify types):
   ```
   Field Name               Type            Notes
   ─────────────────────────────────────────────────────
   id                       Text            Primary Key ✓
   FirstName                Text            
   LastName                 Text            
   Name                     Text            
   Email                    Text/Email      Use Email type if available
   Phone                    Text            
   email_opens              Number          
   email_clicks             Number          
   email_bounces            Number          
   sms_opens                Number          
   whatsapp_reads           Number          
   push_opens               Number          
   website_product_views    Number          
   website_purchases        Number          
   total_order_value        Number/Currency Decimal(10,2)
   omnichannel_score        Number          Decimal(3,2)
   engagement_score         Number          Integer
   preferred_channel        Text            
   favorite_category        Text            
   last_engagement_date     DateTime        ISO 8601
   ```

7. **Save & Activate:**
   - Review mappings
   - Click **"Save & Activate"**
   - ⏳ Wait 30 seconds - 2 minutes for processing

#### **STEP 3: Upload Individual Insights Data (2 minutes)**

1. **Create New Data Stream:**
   - Data Streams → **"New"**
   - Choose **"Upload"** or **"CSV Upload"**

2. **Upload File:**
   - Select: **`individual_insights.csv`**
   - Click **"Upload"**

3. **Configure Stream:**
   - **Stream Name:** `Individual_Insights_Stream`
   - **Data Lake Object Name:** `Individual_Insights`
   - **Description:** "Time-series behavioral insights - 529 records"
   - Click **Next**

4. **Set Composite Primary Key:** ⚠️ IMPORTANT
   - **Primary Key Type:** Composite
   - **Field 1:** `Individual_Id` (Text)
   - **Field 2:** `Event_Timestamp` (DateTime)
   - This ensures uniqueness per individual per timestamp
   - Click **Next**

5. **Map Fields:**
   ```
   Field Name               Type            Notes
   ─────────────────────────────────────────────────────
   Individual_Id            Text            Primary Key 1 (Foreign Key)
   Event_Timestamp          DateTime        Primary Key 2 (ISO 8601)
   Individual_Name          Text            
   Individual_Email         Text/Email      
   Individual_Phone         Text            
   Current_Sentiment        Text            
   Lifestyle_Quotient       Text            
   Health_Profile           Text            
   Fitness_Milestone        Text            
   Purchase_Intent          Text            
   Favourite_Brand          Text            
   Favourite_Destination    Text            
   Hobby                    Text            
   Imminent_Event           Text            Long Text
   data_source              Text            
   ```

6. **Save & Activate:**
   - Click **"Save & Activate"**
   - ⏳ Wait for processing

#### **STEP 4: Create Relationship Between Objects (30 seconds)**

1. **Navigate to Data Model:**
   - Click **Data Model** tab
   - Find **`Individual_Insights`** object
   - Click on it to open details

2. **Add Relationship:**
   - Click **"Relationships"** or **"Add Relationship"**
   - **Relationship Type:** Many-to-One
   - **Related Object:** `Individual_Engagement`
   - **Foreign Key Field:** `Individual_Id`
   - **Related Object Field:** `id`
   - **Relationship Name:** `Engagement` or `Individual`
   - **Description:** "Links insights to individual engagement records"
   - Click **"Save"**

#### **STEP 5: Verify Data Upload (1 minute)**

1. **Open Query Studio:**
   - Click **Query** tab or **Data Explorer**
   - Or: Setup → Data Cloud → Query

2. **Run Verification Queries:**

```sql
-- ✅ Check Individual Engagement upload
SELECT COUNT(*) as Total_Records
FROM Individual_Engagement;
-- Expected: 100

-- ✅ Check Individual Insights upload
SELECT COUNT(*) as Total_Records
FROM Individual_Insights;
-- Expected: 529

-- ✅ Find your record
SELECT 
    Name,
    Email,
    Phone,
    omnichannel_score,
    email_opens,
    preferred_channel
FROM Individual_Engagement
WHERE Email = 'bbanerjee@salesforce.com';
-- Expected: 1 record, Score: 6.88

-- ✅ Verify relationship
SELECT 
    e.Name,
    e.Email,
    e.omnichannel_score,
    i.Current_Sentiment,
    i.Purchase_Intent,
    i.Event_Timestamp
FROM Individual_Engagement e
JOIN Individual_Insights i ON e.id = i.Individual_Id
WHERE e.Email = 'bbanerjee@salesforce.com'
ORDER BY i.Event_Timestamp DESC
LIMIT 5;
-- Expected: 5 most recent insights for Biswarup

-- ✅ Top 10 engaged individuals
SELECT 
    Name,
    Email,
    omnichannel_score,
    preferred_channel,
    email_opens,
    website_purchases
FROM Individual_Engagement
ORDER BY omnichannel_score DESC
LIMIT 10;
-- Expected: Biswarup Banerjee at #1
```

3. **Success Indicators:**
   - ✅ 100 records in Individual_Engagement
   - ✅ 529 records in Individual_Insights
   - ✅ Your record (bbanerjee@salesforce.com) visible
   - ✅ JOIN query returns results
   - ✅ No error messages in Data Streams

---

## **PATH 2: CLI-Based Upload (Programmatic)**

Perfect for: Automation, scripting, repeatable uploads

### **Prerequisites:**
```bash
# Install Salesforce CLI
brew install sf

# Or download from:
# https://developer.salesforce.com/tools/salesforcecli
```

### **Step-by-Step:**

#### **STEP 1: Connect to Data Cloud Org**

```bash
# Login via web browser (easiest)
sf org login web --alias datacloud-sftutor

# Or use username/password
sf org login user \
  --username your.email@company.com \
  --password yourpassword \
  --alias datacloud-sftutor

# Verify connection
sf org display --target-org datacloud-sftutor
```

#### **STEP 2: Upload via Bulk API**

```bash
cd "/Users/bbanerjee/.cursor/DC MCP/datacloud_app"

# Upload Individual Engagement
sf data import csv \
  --file data/synthetic_engagement.csv \
  --sobject IndividualEngagement__c \
  --target-org datacloud-sftutor

# Upload Individual Insights
sf data import csv \
  --file data/individual_insights.csv \
  --sobject IndividualInsights__c \
  --target-org datacloud-sftutor
```

#### **STEP 3: Use Python Upload Script**

We've created a ready-to-use Python script:

```bash
# Check if script exists
ls upload_to_datacloud.py

# If exists, run it:
python3 upload_to_datacloud.py

# Follow on-screen prompts
```

**The script will:**
1. Connect to your Salesforce org
2. Validate CSV files
3. Create Data Cloud objects (if needed)
4. Upload data via Bulk API
5. Verify upload completion
6. Display summary

---

## **PATH 3: S3-Based Ingestion (Enterprise)**

Perfect for: Continuous sync, large-scale data, scheduled updates

### **Step-by-Step:**

#### **STEP 1: Upload CSVs to S3**

```bash
# Install AWS CLI (if needed)
brew install awscli

# Configure AWS credentials
aws configure

# Create S3 bucket (if needed)
aws s3 mb s3://datacloud-uploads

# Upload files
aws s3 cp data/synthetic_engagement.csv s3://datacloud-uploads/engagement/
aws s3 cp data/individual_insights.csv s3://datacloud-uploads/insights/
```

#### **STEP 2: Configure S3 Data Stream in Data Cloud**

1. **In Data Cloud:**
   - Data Streams → New → **Amazon S3**

2. **Configure Connection:**
   - **Connection Name:** AWS_DataCloud_Connector
   - **Bucket:** datacloud-uploads
   - **Region:** us-east-1 (or your region)
   - **Access Key ID:** (from AWS IAM)
   - **Secret Access Key:** (from AWS IAM)
   - Test connection → **Save**

3. **Create Engagement Stream:**
   - **Source:** S3 Connection
   - **Bucket Path:** `engagement/`
   - **File Pattern:** `*.csv`
   - **Schedule:** Daily at 2:00 AM (or real-time)
   - Map fields (same as PATH 1)

4. **Create Insights Stream:**
   - **Source:** S3 Connection
   - **Bucket Path:** `insights/`
   - **File Pattern:** `*.csv`
   - Map fields (same as PATH 1)

#### **STEP 3: Enable Continuous Sync**

- Set schedule: **Daily** or **Real-time**
- Enable **Incremental Updates** (only new records)
- Configure **Error Handling** (email alerts)

---

## 🎯 POST-INGESTION STEPS

### **1. Configure Identity Resolution**

**Purpose:** Link multiple data sources to a unified individual profile

```sql
-- In Data Cloud → Identity Resolution

Rule 1: Email Matching
├─ Match Field: Email
├─ Source: Individual_Engagement
├─ Priority: High
└─ Algorithm: Exact Match

Rule 2: Phone Matching
├─ Match Field: Phone
├─ Source: Individual_Engagement
├─ Priority: Medium
└─ Algorithm: Normalized Match

Rule 3: Salesforce ID Matching
├─ Match Field: id
├─ Source: Individual_Engagement
├─ Priority: High
└─ Algorithm: Exact Match
```

### **2. Create Calculated Insights**

Create derived fields:

```sql
-- Total Engagement Score
(email_opens * 2) + (email_clicks * 3) + (website_purchases * 10)

-- Omnichannel Participation
COUNT(DISTINCT preferred_channel)

-- Recent High Intent Indicator
CASE 
  WHEN Purchase_Intent IN ('Very High', 'Immediate') 
    AND Event_Timestamp >= CURRENT_DATE - 7 
  THEN 'Hot Lead'
  ELSE 'Normal'
END
```

### **3. Build Segments**

#### **VIP Customers:**
```sql
SELECT * FROM Individual_Engagement
WHERE omnichannel_score >= 6.0
```

#### **High Purchase Intent (Last 7 Days):**
```sql
SELECT DISTINCT 
    e.Name,
    e.Email,
    e.Phone,
    i.Purchase_Intent,
    i.Current_Sentiment
FROM Individual_Engagement e
JOIN Individual_Insights i ON e.id = i.Individual_Id
WHERE i.Purchase_Intent IN ('Very High', 'Immediate')
  AND i.Event_Timestamp >= CURRENT_DATE - 7
ORDER BY e.omnichannel_score DESC
```

#### **Email Engaged:**
```sql
SELECT * FROM Individual_Engagement
WHERE preferred_channel = 'Email'
  AND email_opens > 15
```

#### **Frustrated Customers Needing Support:**
```sql
SELECT DISTINCT 
    e.Name,
    e.Email,
    i.Current_Sentiment,
    COUNT(*) as Frustrated_Count
FROM Individual_Engagement e
JOIN Individual_Insights i ON e.id = i.Individual_Id
WHERE i.Current_Sentiment = 'Frustrated'
  AND i.Event_Timestamp >= CURRENT_DATE - 30
GROUP BY e.Name, e.Email, i.Current_Sentiment
HAVING COUNT(*) >= 3
ORDER BY Frustrated_Count DESC
```

### **4. Create Activations**

#### **Email Campaign Activation:**

1. **Navigate:** Data Cloud → Activations → New
2. **Configure:**
   - **Name:** VIP_Email_Campaign
   - **Target:** Marketing Cloud Email Studio
   - **Segment:** VIP Customers (score >= 6.0)
   - **Schedule:** Daily at 9:00 AM
3. **Map Fields:**
   ```
   FirstName          → {{firstName}}
   Email              → {{email}}
   omnichannel_score  → {{vipScore}}
   favorite_category  → {{favCategory}}
   preferred_channel  → {{channel}}
   ```
4. **Activate**

#### **SMS Campaign Activation:**

1. **Target:** Marketing Cloud Mobile Studio
2. **Segment:** High Purchase Intent
3. **Map Fields:** Phone, FirstName, Purchase_Intent
4. **Send to:** +91 phone numbers

---

## ✅ SUCCESS CHECKLIST

- [ ] **Data Upload Complete**
  - [ ] Individual_Engagement: 100 records ✅
  - [ ] Individual_Insights: 529 records ✅

- [ ] **Data Verification**
  - [ ] Found Biswarup Banerjee record ✅
  - [ ] All 100 names visible ✅
  - [ ] Relationship working (JOIN query succeeds) ✅

- [ ] **Identity Resolution**
  - [ ] Email matching configured ✅
  - [ ] Phone matching configured ✅

- [ ] **Segments Created**
  - [ ] VIP Customers segment ✅
  - [ ] High Purchase Intent segment ✅
  - [ ] Email Engaged segment ✅

- [ ] **Activations**
  - [ ] Email campaign activation ✅
  - [ ] SMS campaign activation ✅

---

## 🔧 TROUBLESHOOTING

### **Issue: "Primary Key Violation"**
**Cause:** Duplicate records in CSV  
**Solution:**
```bash
# Check for duplicates in Engagement
python3 -c "
import csv
rows = list(csv.DictReader(open('data/synthetic_engagement.csv')))
ids = [r['id'] for r in rows]
print(f'Total: {len(ids)}, Unique: {len(set(ids))}')
print(f'Duplicates: {len(ids) - len(set(ids))}')
"

# Check for duplicates in Insights (composite key)
python3 -c "
import csv
rows = list(csv.DictReader(open('data/individual_insights.csv')))
keys = [(r['Individual_Id'], r['Event_Timestamp']) for r in rows]
print(f'Total: {len(keys)}, Unique: {len(set(keys))}')
print(f'Duplicates: {len(keys) - len(set(keys))}')
"
```

### **Issue: "Field Type Mismatch"**
**Cause:** DateTime not in correct format  
**Solution:** Verify format is ISO 8601: `2025-10-31T08:43:59`

```bash
# Check datetime format
head -2 data/individual_insights.csv | grep -o "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T"
```

### **Issue: "Can't See Data After Upload"**
**Cause:** Data processing delay  
**Solution:**
- ⏳ Wait 2-5 minutes
- Refresh Data Streams page
- Check **Data Processing Jobs** for status
- Look for errors in **Monitoring** → **Jobs**

### **Issue: "Relationship Not Working"**
**Cause:** Foreign key mismatch  
**Solution:**
```sql
-- Verify IDs exist in both tables
SELECT DISTINCT Individual_Id 
FROM Individual_Insights
WHERE Individual_Id NOT IN (SELECT id FROM Individual_Engagement);
-- Should return 0 rows
```

### **Issue: "UTF-8 Encoding Errors"**
**Cause:** File encoding not UTF-8  
**Solution:**
```bash
# Convert to UTF-8
iconv -f UTF-8 -t UTF-8 data/synthetic_engagement.csv > data/engagement_utf8.csv
iconv -f UTF-8 -t UTF-8 data/individual_insights.csv > data/insights_utf8.csv
```

---

## 📂 FILE LOCATIONS

All files ready for upload:

```
/Users/bbanerjee/.cursor/DC MCP/datacloud_app/
├── data/
│   ├── synthetic_engagement.csv    (100 records, 54 KB)
│   ├── synthetic_engagement.json   (Original format)
│   ├── individual_insights.csv     (529 records, 129 KB)
│   └── individual_insights.json    (Original format)
├── DATA_CLOUD_UPLOAD_GUIDE.md      (Detailed guide)
├── QUICK_UPLOAD_STEPS.md           (5-minute quickstart)
├── DATA_CLOUD_INSIGHTS_SETUP.md    (Insights schema)
├── upload_to_datacloud.py          (Python script)
└── MASTER_DATA_INGESTION_PATH.md   (This file)
```

---

## 📊 EXPECTED RESULTS AFTER INGESTION

### **Data Cloud Unified Profile - Biswarup Banerjee**

**Contact Information:**
- 📧 Email: bbanerjee@salesforce.com
- 📱 Phone: +919154321430
- 🆔 Individual ID: 0PKKX000000Tfjv4AC

**Engagement Summary:**
- ⭐ Omnichannel Score: 6.88/10 (#1 Ranked)
- 📧 Email Opens: 18 | Clicks: 15
- 📱 SMS Opens: 20 | Clicks: 13
- 💬 WhatsApp Reads: 15 | Replies: 11
- 🔔 Push Opens: 22 | Clicks: 11
- 🌐 Website: 28 views, 9 purchases, $492.92 total
- 🎯 Preferred Channel: Email
- ❤️ Favorite Category: Electronics

**Behavioral Insights (6 records over 90 days):**
- Most Recent Sentiment: Anxious
- Lifestyle: Luxury Seeker
- Health: Hypertensive
- Purchase Intent: Considering
- Favorite Brand: Samsung
- Dream Destination: Maldives
- Hobby: Reading
- Next Event: Baby shower for sister this Sunday

---

## 🎉 SUCCESS!

After completing this ingestion path, your Data Cloud org will contain:

✅ **100 Individuals** with complete profiles  
✅ **529 Behavioral Insights** tracking changes over time  
✅ **Real Indian Names** and contact information  
✅ **Omnichannel Engagement** across 5 channels  
✅ **Your VIP Profile** as #1 most engaged customer  
✅ **Relationships** linking insights to individuals  
✅ **Ready for Segmentation** and activation  

**You can now:**
- 🎯 Create data-driven segments
- 📧 Launch personalized campaigns
- 📊 Track engagement trends
- 🔮 Monitor behavioral insights
- 🚀 Activate across Marketing Cloud

---

## 📞 SUPPORT & RESOURCES

- **📖 Data Cloud Docs:** https://help.salesforce.com/s/articleView?id=sf.c360_a_data_cloud.htm
- **🎓 Trailhead:** Search "Data Cloud Basics"
- **💬 Community:** Salesforce Data Cloud Trailblazer Community
- **🔧 GitHub:** Upload script at `upload_to_datacloud.py`

---

**Generated:** October 31, 2025  
**Application:** Data Cloud Management App  
**Location:** `/Users/bbanerjee/.cursor/DC MCP/datacloud_app/`

**🚀 Ready to ingest! Choose PATH 1 for quickest results!**


