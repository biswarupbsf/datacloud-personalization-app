# 🚀 Quick Upload to Data Cloud - 5 Simple Steps

## 📂 Files Ready for Upload

✅ **2 CSV files ready** at:
```
/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/synthetic_engagement.csv (100 individuals)
/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/individual_insights.csv (529 insights)
```

---

## ⚡ QUICK START (5 Minutes)

### **STEP 1: Open Your Data Cloud Org** (30 seconds)

1. Go to your Salesforce org: **https://login.salesforce.com**
2. Login with your credentials
3. Open the **App Launcher** (grid icon, top-left)
4. Search for and select **"Data Cloud"**

---

### **STEP 2: Upload Engagement Data** (2 minutes)

1. **Navigate to Data Streams:**
   - Click **Data Streams** tab
   - Click **"New Data Stream"**

2. **Select Upload Method:**
   - Choose **"Upload"** or **"File Upload"**
   - Click **Next**

3. **Upload CSV File:**
   - Click **"Choose File"**
   - Navigate to: `/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/`
   - Select: **synthetic_engagement.csv**
   - Click **"Open"** and **"Upload"**

4. **Configure Data Stream:**
   - **Name:** `Individual_Engagement_Stream`
   - **Data Lake Object:** `Individual_Engagement`
   - Click **Next**

5. **Map Primary Key:**
   - **Primary Key Field:** Select `id`
   - **Data Type:** Text
   - Click **Next**

6. **Field Mapping** (Auto-detected, just verify):
   ```
   FirstName          → Text
   LastName           → Text
   Name               → Text
   Email              → Text (or Email type if available)
   Phone              → Text
   email_opens        → Number
   email_clicks       → Number
   omnichannel_score  → Number (Decimal)
   preferred_channel  → Text
   favorite_category  → Text
   ```

7. **Activate:**
   - Click **"Save & Activate"**
   - Wait for processing (30 seconds - 2 minutes)

---

### **STEP 3: Upload Insights Data** (2 minutes)

Repeat Step 2 with these settings:

1. **Upload File:** `individual_insights.csv`

2. **Configure:**
   - **Name:** `Individual_Insights_Stream`
   - **Data Lake Object:** `Individual_Insights`

3. **Primary Key:** **COMPOSITE KEY**
   - **Field 1:** `Individual_Id` (Text)
   - **Field 2:** `Event_Timestamp` (DateTime)

4. **Field Mapping:**
   ```
   Individual_Id          → Text
   Event_Timestamp        → DateTime
   Individual_Name        → Text
   Individual_FirstName   → Text
   Individual_LastName    → Text
   Individual_Email       → Text
   Individual_Phone       → Text
   Current_Sentiment      → Text
   Lifestyle_Quotient     → Text
   Health_Profile         → Text
   Fitness_Milestone      → Text
   Purchase_Intent        → Text
   Favourite_Brand        → Text
   Favourite_Destination  → Text
   Hobby                  → Text
   Imminent_Event         → Text
   ```

5. **Activate:** Click **"Save & Activate"**

---

### **STEP 4: Create Relationship** (30 seconds)

1. **Go to Data Model:**
   - Click **Data Model** tab
   - Find **Individual_Insights**

2. **Add Relationship:**
   - Click **"Add Relationship"**
   - **Related Object:** Individual_Engagement
   - **Foreign Key:** Individual_Id
   - **Related Field:** id
   - **Relationship Name:** Engagement
   - Click **"Save"**

---

### **STEP 5: Verify Upload** (30 seconds)

1. **Open Query Studio:**
   - Click **Query** tab or **Data Explorer**

2. **Run Verification Queries:**

```sql
-- Check engagement data
SELECT COUNT(*) as Total FROM Individual_Engagement;
-- Expected: 100

-- Check insights data  
SELECT COUNT(*) as Total FROM Individual_Insights;
-- Expected: 529

-- Find Biswarup Banerjee
SELECT Name, Email, Phone, omnichannel_score 
FROM Individual_Engagement 
WHERE Email = 'bbanerjee@salesforce.com';
-- Expected: 1 record with score 6.88

-- Top 10 engaged individuals
SELECT Name, Email, omnichannel_score 
FROM Individual_Engagement 
ORDER BY omnichannel_score DESC 
LIMIT 10;
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Logged into Data Cloud
- [ ] Uploaded synthetic_engagement.csv (100 records)
- [ ] Uploaded individual_insights.csv (529 records)
- [ ] Created relationship between objects
- [ ] Verified record counts
- [ ] Found your record (bbanerjee@salesforce.com)

---

## 🎯 What You Can Do Now

### **1. View Your Profile**
```sql
SELECT 
    Name,
    Email,
    Phone,
    omnichannel_score,
    email_opens,
    email_clicks,
    website_purchases,
    preferred_channel,
    favorite_category
FROM Individual_Engagement
WHERE Email = 'bbanerjee@salesforce.com';
```

### **2. Create a VIP Segment**
```sql
SELECT * FROM Individual_Engagement
WHERE omnichannel_score >= 6.0
ORDER BY omnichannel_score DESC;
```

### **3. View Your Insights Over Time**
```sql
SELECT 
    Event_Timestamp,
    Current_Sentiment,
    Purchase_Intent,
    Lifestyle_Quotient,
    Imminent_Event
FROM Individual_Insights
WHERE Individual_Email = 'bbanerjee@salesforce.com'
ORDER BY Event_Timestamp DESC;
```

### **4. High Purchase Intent Individuals**
```sql
SELECT DISTINCT
    i.Individual_Name,
    i.Individual_Email,
    i.Purchase_Intent,
    i.Current_Sentiment
FROM Individual_Insights i
WHERE i.Purchase_Intent IN ('Very High', 'Immediate')
ORDER BY i.Event_Timestamp DESC;
```

---

## 🚨 Troubleshooting

### **Problem: CSV Upload Button Not Found**
**Solution:** Make sure you're in the Data Cloud app, not Service Cloud or Sales Cloud

### **Problem: Field Mapping Errors**
**Solution:** 
- Check that DateTime fields are in format: `2025-10-31T08:43:59`
- Number fields should not have quotes
- Use UTF-8 encoding

### **Problem: Can't See Uploaded Data**
**Solution:** 
- Wait 2-5 minutes for processing
- Click **Refresh** in Data Streams
- Check **Data Processing Jobs** for status

### **Problem: "Primary Key Violation"**
**Solution:** 
- For Individual_Engagement: Use `id` (unique)
- For Individual_Insights: Use composite key (Individual_Id + Event_Timestamp)

---

## 📞 Need Help?

- **Data Cloud Documentation:** https://help.salesforce.com/s/articleView?id=sf.c360_a_data_cloud.htm
- **Upload Guide:** See `DATA_CLOUD_UPLOAD_GUIDE.md` for detailed instructions
- **Programmatic Upload:** See `upload_to_datacloud.py` for API-based upload

---

## 🎉 You're Done!

Your Data Cloud org now contains:
- ✅ 100 individuals with complete engagement data
- ✅ 529 time-series insights tracking behavior over 90 days
- ✅ Your VIP profile (Biswarup Banerjee) as #1 most engaged
- ✅ Real Indian names, emails, and phone numbers
- ✅ Omnichannel engagement (Email, SMS, WhatsApp, Push, Website)

**Ready to create segments and activate campaigns!** 🚀



