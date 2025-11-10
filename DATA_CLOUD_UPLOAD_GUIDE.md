# 🚀 Data Cloud Upload Guide - CSV Files

## 📂 Available CSV Files for Upload

1. **synthetic_engagement.csv** (54 KB)
   - 100 individuals with omnichannel engagement data
   - Includes: Email, SMS, WhatsApp, Push, Website engagement
   - Contact info: Names, emails, phone numbers

2. **individual_insights.csv** (129 KB)
   - 529 time-series insight records
   - Tracks sentiment, lifestyle, health, purchase intent over time
   - Links to individuals via Individual_Id

---

## 🔗 STEP 1: Connect to Salesforce Data Cloud Org

### **Option A: Using Salesforce CLI (Recommended)**

#### 1. Install Salesforce CLI (if not already installed)
```bash
# macOS
brew install sf

# Or download from: https://developer.salesforce.com/tools/salesforcecli
```

#### 2. Login to Your Data Cloud Org
```bash
sf org login web --alias datacloud-sftutor
```

This will:
- Open a browser window
- Prompt you to login to your Salesforce org
- Save the connection for future use

#### 3. Verify Connection
```bash
sf org display --target-org datacloud-sftutor
```

### **Option B: Using Username/Password (API Access)**

If you have API access enabled:
```bash
sf org login user \
  --username your.email@company.com \
  --password yourpassword \
  --alias datacloud-sftutor
```

---

## 📊 STEP 2: Upload Data to Data Cloud

### **Method 1: Using Data Cloud UI (Easiest)**

#### **Upload Engagement Data:**

1. **Login to Data Cloud**
   - Go to your Salesforce org
   - Navigate to **Data Cloud** app

2. **Create Data Stream**
   - Go to **Data Streams** tab
   - Click **New Data Stream**
   - Select **Upload CSV**

3. **Configure Data Stream:**
   - **Name:** Individual_Engagement_Stream
   - **Source:** Upload CSV
   - **Upload File:** Select `data/synthetic_engagement.csv`

4. **Map Fields:**
   ```
   CSV Column           → Data Cloud Field Type
   ──────────────────────────────────────────────
   id                   → Text (Primary Key)
   FirstName            → Text
   LastName             → Text
   Name                 → Text
   Email                → Email
   Phone                → Phone
   email_opens          → Number
   email_clicks         → Number
   email_bounces        → Number
   sms_opens            → Number
   whatsapp_reads       → Number
   push_opens           → Number
   website_product_views → Number
   website_purchases    → Number
   total_order_value    → Currency
   omnichannel_score    → Number
   preferred_channel    → Text
   favorite_category    → Text
   ```

5. **Create Data Model Object:**
   - **Object Name:** Individual_Engagement__dlm
   - **Primary Key:** id
   - Click **Save & Activate**

#### **Upload Insights Data:**

Repeat the same process for `individual_insights.csv`:

1. **Create Data Stream**
   - **Name:** Individual_Insights_Stream
   - **Upload File:** `data/individual_insights.csv`

2. **Map Fields:**
   ```
   CSV Column              → Data Cloud Field Type
   ───────────────────────────────────────────────
   Individual_Id           → Text (Foreign Key)
   Event_Timestamp         → DateTime
   Current_Sentiment       → Text
   Lifestyle_Quotient      → Text
   Health_Profile          → Text
   Fitness_Milestone       → Text
   Purchase_Intent         → Text
   Favourite_Brand         → Text
   Favourite_Destination   → Text
   Hobby                   → Text
   Imminent_Event          → Text
   ```

3. **Set Primary Key:**
   - **Primary Key:** Composite (Individual_Id + Event_Timestamp)

4. **Create Relationship:**
   - **Related Object:** Individual_Engagement__dlm
   - **Foreign Key:** Individual_Id
   - **Related Field:** id

---

### **Method 2: Using Bulk API (Programmatic)**

I've created a Python script to upload via Salesforce Bulk API.

#### **Run the Upload Script:**

```bash
cd "/Users/bbanerjee/.cursor/DC MCP/datacloud_app"
python3 upload_to_datacloud.py
```

This script will:
1. Connect to your Salesforce org
2. Create custom objects for the data
3. Upload both CSV files via Bulk API
4. Show progress and results

---

### **Method 3: Using S3 Integration (For Ongoing Sync)**

If you want continuous data sync:

1. **Upload CSVs to S3:**
   ```bash
   aws s3 cp data/synthetic_engagement.csv s3://your-bucket/datacloud/
   aws s3 cp data/individual_insights.csv s3://your-bucket/datacloud/
   ```

2. **Configure S3 Data Stream in Data Cloud:**
   - Go to **Data Streams** → **New**
   - Select **Amazon S3**
   - Configure connection:
     - **Bucket:** your-bucket
     - **Prefix:** datacloud/
     - **File Pattern:** *.csv
     - **Schedule:** Daily (or real-time)

3. **Map Fields** (same as Method 1)

---

## 🔄 STEP 3: Identity Resolution

After uploading, configure identity resolution:

### **Link Individuals to Unified Profile:**

1. **Go to Identity Resolution**
   - Data Cloud → Identity Resolution

2. **Create Resolution Rule:**
   - **Name:** Individual_Email_Match
   - **Match Field:** Email
   - **Source Object:** Individual_Engagement__dlm
   - **Priority:** High

3. **Add Phone Match:**
   - **Name:** Individual_Phone_Match
   - **Match Field:** Phone
   - **Source Object:** Individual_Engagement__dlm
   - **Priority:** Medium

4. **Save & Activate**

---

## 📈 STEP 4: Verify Upload

### **Check Record Counts:**

```sql
-- In Data Cloud Query Studio

-- Check engagement records
SELECT COUNT(*) as Total_Individuals 
FROM Individual_Engagement__dlm;
-- Expected: 100

-- Check insights records
SELECT COUNT(*) as Total_Insights 
FROM Individual_Insights__dlm;
-- Expected: 529

-- Check Biswarup's record
SELECT Name, Email, Phone, omnichannel_score 
FROM Individual_Engagement__dlm 
WHERE Email = 'bbanerjee@salesforce.com';
-- Expected: 1 record with your details
```

### **View Sample Data:**

```sql
-- Top 10 engaged individuals
SELECT 
    Name, 
    Email, 
    Phone, 
    omnichannel_score,
    preferred_channel
FROM Individual_Engagement__dlm
ORDER BY omnichannel_score DESC
LIMIT 10;
```

### **View Insights Over Time:**

```sql
-- Recent insights for Biswarup
SELECT 
    Individual_Name,
    Event_Timestamp,
    Current_Sentiment,
    Purchase_Intent,
    Imminent_Event
FROM Individual_Insights__dlm
WHERE Individual_Email = 'bbanerjee@salesforce.com'
ORDER BY Event_Timestamp DESC
LIMIT 10;
```

---

## 🎯 STEP 5: Create Segments

Once data is loaded, create segments:

### **Example Segments:**

#### **1. VIP Customers (High Engagement)**
```sql
SELECT * FROM Individual_Engagement__dlm
WHERE omnichannel_score >= 6.0
```

#### **2. High Purchase Intent**
```sql
SELECT DISTINCT 
    e.Name,
    e.Email,
    e.Phone,
    i.Purchase_Intent
FROM Individual_Engagement__dlm e
JOIN Individual_Insights__dlm i ON e.id = i.Individual_Id
WHERE i.Purchase_Intent IN ('Very High', 'Immediate')
  AND i.Event_Timestamp >= CURRENT_DATE - 7
```

#### **3. Email Preferred Channel**
```sql
SELECT * FROM Individual_Engagement__dlm
WHERE preferred_channel = 'Email'
  AND email_opens > 15
```

---

## 📱 STEP 6: Activate for Marketing

### **Create Activation for Email Campaign:**

1. **Go to Activations**
   - Data Cloud → Activations → New

2. **Configure Activation:**
   - **Name:** VIP_Email_Campaign
   - **Target:** Email
   - **Segment:** VIP Customers (omnichannel_score >= 6.0)
   - **Personalization Fields:**
     - FirstName
     - Email
     - omnichannel_score
     - favorite_category
     - preferred_channel

3. **Connect to Marketing Cloud:**
   - Select Marketing Cloud Journey Builder
   - Map fields to journey entry source

4. **Activate**

---

## 🔧 Troubleshooting

### **Issue: CSV Upload Failed**
- **Solution:** Check file encoding (must be UTF-8)
- **Fix:** 
  ```bash
  iconv -f UTF-8 -t UTF-8 data/synthetic_engagement.csv > data/engagement_utf8.csv
  ```

### **Issue: Field Mapping Errors**
- **Solution:** Ensure all field types match
- **Check:** Date fields must be in ISO format (YYYY-MM-DDTHH:MM:SS)

### **Issue: Primary Key Constraint Violation**
- **Solution:** Ensure Individual_Id + Event_Timestamp is unique
- **Verify:**
  ```bash
  python3 -c "import csv; rows = list(csv.DictReader(open('data/individual_insights.csv'))); keys = [(r['Individual_Id'], r['Event_Timestamp']) for r in rows]; print(f'Duplicates: {len(keys) - len(set(keys))}')"
  ```

### **Issue: Can't See Data in Data Cloud**
- **Solution:** Wait 5-10 minutes for data processing
- **Refresh:** Data Cloud → Data Streams → Refresh

---

## 📊 File Locations

All CSV files ready for upload:

```
/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/synthetic_engagement.csv
/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/individual_insights.csv
```

---

## ✅ Success Checklist

- [ ] Connected to Data Cloud org
- [ ] Created Individual_Engagement__dlm Data Stream
- [ ] Created Individual_Insights__dlm Data Stream
- [ ] Uploaded synthetic_engagement.csv (100 records)
- [ ] Uploaded individual_insights.csv (529 records)
- [ ] Configured Identity Resolution
- [ ] Verified record counts
- [ ] Found Biswarup Banerjee record
- [ ] Created test segment
- [ ] Created activation

---

## 🎉 Next Steps After Upload

1. **View Your Profile:**
   - Search for: bbanerjee@salesforce.com
   - See your engagement score: 6.88/10
   - View your insights over time

2. **Create Segments:**
   - VIP customers (high engagement)
   - High purchase intent
   - Channel preferences

3. **Activate Campaigns:**
   - Send personalized emails
   - SMS campaigns to Indian phone numbers
   - WhatsApp messaging

4. **Monitor Performance:**
   - Track engagement trends
   - Monitor sentiment changes
   - Identify purchase intent signals

---

For detailed API upload, see: `upload_to_datacloud.py`





