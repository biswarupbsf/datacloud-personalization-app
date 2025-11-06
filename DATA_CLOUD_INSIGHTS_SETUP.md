# 🔮 Individual Insights Data Object - Setup Guide

## Overview
The **Individual_Insights** object tracks behavioral, emotional, and lifestyle insights about individuals over time. This is a **time-series dataset** where each individual can have multiple records at different timestamps.

---

## 📊 Object Schema

### **Object Name:** `Individual_Insights__dlm`

### **Primary Key:** Composite key of `Individual_Id` + `Event_Timestamp`

### **Fields:**

| Field Name | Data Type | Description | Sample Values |
|------------|-----------|-------------|---------------|
| **Individual_Id** | Text (18) | Foreign key to Individual object | 0PKKX000000TfiT4AS |
| **Event_Timestamp** | DateTime | When the insight was captured | 2025-10-23T18:20:48 |
| **Current_Sentiment** | Text (50) | Emotional state | Happy, Sad, Elated, Frustrated, Disgusted, Angry, Excited, Anxious, Calm, Stressed |
| **Lifestyle_Quotient** | Text (50) | Lifestyle category | Careerist, Traveller, Foodie, Connoisseur, Homebody, Adventurer, Minimalist, Luxury Seeker, Health Enthusiast, Tech Savvy |
| **Health_Profile** | Text (50) | Health status | Sick, Athletic, Stressed, Hypertensive, Hypotensive, Healthy, Recovering, Fit, Active, Sedentary |
| **Fitness_Milestone** | Text (50) | Fitness level | Rookie, Amateur, Professional, Elite, Beginner, Intermediate, Advanced, Champion |
| **Purchase_Intent** | Text (50) | Likelihood to purchase | Very High, Immediate, High, Medium, Tepid, Low, Not Interested, Considering, Researching |
| **Favourite_Brand** | Text (100) | Preferred brand | Apple, Nike, Tesla, Starbucks, etc. |
| **Favourite_Destination** | Text (100) | Travel preference | Paris, Tokyo, Bali, Hawaii, etc. |
| **Hobby** | Text (100) | Primary hobby | Reading, Hiking, Photography, Cooking, etc. |
| **Imminent_Event** | Text (255) | Upcoming event/activity | "Watch Soccer match final with friends today" |
| **data_source** | Text (50) | Source of data | synthetic_insights |

---

## 📈 Generated Data Summary

✅ **529 insight records** generated for **100 individuals**

### Key Statistics:
- **Average Records per Individual:** 5.29
- **Time Range:** Last 90 days
- **Data Pattern:** Time-series (multiple records per individual)

### Top Sentiments:
1. Frustrated (76 records)
2. Sad (68 records)
3. Anxious (61 records)
4. Angry (56 records)
5. Excited (54 records)

### Top Lifestyles:
1. Homebody (88 records)
2. Adventurer (73 records)
3. Luxury Seeker (62 records)
4. Traveller (54 records)
5. Connoisseur (53 records)

### Top Purchase Intents:
1. Very High (77 records)
2. Researching (70 records)
3. High (67 records)
4. Medium (63 records)
5. Immediate (55 records)

---

## 🚀 Setup Instructions

### **Step 1: Create Data Lake Model Object in Salesforce Data Cloud**

1. **Login to Salesforce Data Cloud (SFtutor org)**
   ```
   sf org login web --alias sftutor
   ```

2. **Navigate to Data Cloud Setup**
   - Go to **Setup** → **Data Cloud** → **Data Streams**
   - Or use Data Cloud UI directly

3. **Create New Data Lake Model Object**
   - Click **New Data Lake Model Object**
   - **Object Name:** `Individual_Insights__dlm`
   - **Label:** Individual Insights
   - **Description:** Time-series insights tracking sentiment, lifestyle, health, and behavioral data for individuals

4. **Add Fields** (in the same order):
   
   | API Name | Label | Type | Length | Required |
   |----------|-------|------|--------|----------|
   | Individual_Id | Individual ID | Text | 18 | ✓ |
   | Event_Timestamp | Event Timestamp | DateTime | - | ✓ |
   | Current_Sentiment | Current Sentiment | Text | 50 | ✓ |
   | Lifestyle_Quotient | Lifestyle Quotient | Text | 50 | ✓ |
   | Health_Profile | Health Profile | Text | 50 | ✓ |
   | Fitness_Milestone | Fitness Milestone | Text | 50 | ✓ |
   | Purchase_Intent | Purchase Intent | Text | 50 | ✓ |
   | Favourite_Brand | Favourite Brand | Text | 100 | ✓ |
   | Favourite_Destination | Favourite Destination | Text | 100 | ✓ |
   | Hobby | Hobby | Text | 100 | ✓ |
   | Imminent_Event | Imminent Event | Text | 255 | ✓ |
   | data_source | Data Source | Text | 50 | ✓ |

5. **Set Primary Key**
   - **Primary Key Type:** Composite
   - **Key Fields:** `Individual_Id` + `Event_Timestamp`

6. **Create Relationship to Individual**
   - **Relationship Name:** Individual_Insights_to_Individual
   - **Related Object:** Individual__dlm
   - **Foreign Key Field:** Individual_Id
   - **Related Field:** Id

7. **Save and Activate** the Data Lake Model Object

---

### **Step 2: Prepare Data for Upload**

The data has already been generated at:
```
/Users/bbanerjee/.cursor/DC MCP/datacloud_app/data/individual_insights.json
```

**Sample Record:**
```json
{
  "Individual_Id": "0PKKX000000TfiT4AS",
  "Event_Timestamp": "2025-10-23T18:20:48.700636",
  "Current_Sentiment": "Anxious",
  "Lifestyle_Quotient": "Homebody",
  "Health_Profile": "Healthy",
  "Fitness_Milestone": "Elite",
  "Purchase_Intent": "Tepid",
  "Favourite_Brand": "Garmin",
  "Favourite_Destination": "Singapore",
  "Hobby": "Hiking",
  "Imminent_Event": "Picking up new Tesla Model 3 from showroom today",
  "data_source": "synthetic_insights"
}
```

---

### **Step 3: Upload Data to Data Cloud**

#### **Option A: Using Salesforce UI (Data Cloud)**

1. Go to **Data Cloud** → **Data Streams** → **Individual_Insights__dlm**
2. Click **Upload Data**
3. Convert JSON to CSV first:
   ```bash
   cd "/Users/bbanerjee/.cursor/DC MCP/datacloud_app"
   python3 -c "
   import json
   import csv
   
   with open('data/individual_insights.json', 'r') as f:
       data = json.load(f)
   
   with open('data/individual_insights.csv', 'w', newline='') as f:
       writer = csv.DictWriter(f, fieldnames=data[0].keys())
       writer.writeheader()
       writer.writerows(data)
   
   print('✅ CSV created at data/individual_insights.csv')
   "
   ```
4. Upload the CSV file
5. Map fields and import

#### **Option B: Using Salesforce APIs**

Use the Data Cloud Connector API or Bulk API to upload the JSON data programmatically.

#### **Option C: Using S3 Integration**

If you have S3 configured:
1. Upload `individual_insights.json` to S3
2. Configure Data Stream to read from S3
3. Set up incremental sync

---

### **Step 4: Create Identity Resolution Mapping**

1. Go to **Data Cloud** → **Identity Resolution**
2. Map `Individual_Id` to the **Individual** object
3. Enable resolution for cross-object queries

---

### **Step 5: Create Calculated Insights**

#### **Example: Latest Sentiment by Individual**
```sql
SELECT 
    Individual_Id,
    Current_Sentiment,
    Lifestyle_Quotient,
    Purchase_Intent,
    ROW_NUMBER() OVER (PARTITION BY Individual_Id ORDER BY Event_Timestamp DESC) as rn
FROM Individual_Insights__dlm
WHERE rn = 1
```

#### **Example: Purchase Intent Trend**
```sql
SELECT 
    Individual_Id,
    DATE_TRUNC('day', Event_Timestamp) as Date,
    Purchase_Intent,
    COUNT(*) as Observations
FROM Individual_Insights__dlm
WHERE Purchase_Intent IN ('Very High', 'Immediate', 'High')
GROUP BY Individual_Id, Date, Purchase_Intent
```

---

## 🎯 Use Cases

### **1. Sentiment-Based Segmentation**
Create segments based on recent emotional states:
- **Happy & High Purchase Intent** → Send promotional offers
- **Frustrated** → Send support/care messages
- **Excited + Travel Destination** → Send travel deals

### **2. Lifestyle Targeting**
Tailor content based on lifestyle:
- **Careerist + High Fitness** → Professional wellness products
- **Foodie + Traveller** → Culinary travel experiences
- **Health Enthusiast** → Fitness and nutrition content

### **3. Predictive Purchase Intent**
Track purchase intent changes over time:
- **Researching → High → Very High** = Hot lead
- **High → Tepid → Low** = Losing interest (intervention needed)

### **4. Event-Based Personalization**
Use imminent events for timely messaging:
- "Watch Soccer match final" → Send sports merchandise offers
- "Surprise girlfriend with birthday gift" → Gift recommendations
- "Marathon training" → Fitness gear promotions

### **5. Health & Wellness Programs**
Target health-conscious individuals:
- **Athletic + Professional Fitness** → Advanced training programs
- **Stressed + Hypertensive** → Wellness and relaxation content
- **Sick → Recovering** → Recovery support messaging

---

## 📊 Integration with Existing Data

### **Join with Engagement Data**
```sql
SELECT 
    i.Individual_Id,
    i.Current_Sentiment,
    i.Purchase_Intent,
    e.omnichannel_score,
    e.email_opens,
    e.website_purchases
FROM Individual_Insights__dlm i
JOIN synthetic_engagement e ON i.Individual_Id = e.id
WHERE i.Event_Timestamp = (
    SELECT MAX(Event_Timestamp) 
    FROM Individual_Insights__dlm 
    WHERE Individual_Id = i.Individual_Id
)
```

---

## 🔄 Ongoing Data Updates

### **Refresh Frequency Recommendations:**
- **Real-time:** Sentiment, Imminent Events
- **Daily:** Purchase Intent, Health Profile
- **Weekly:** Lifestyle Quotient, Fitness Milestone
- **Monthly:** Favourite Brand, Favourite Destination, Hobby

### **Data Quality Checks:**
1. Ensure timestamps are unique per individual (primary key)
2. Validate sentiment values against allowed list
3. Check for orphaned Individual_Ids
4. Monitor data freshness (no records older than 90 days)

---

## ✅ Verification

After setup, verify with these queries:

### **Check Record Count**
```sql
SELECT COUNT(*) as Total_Records FROM Individual_Insights__dlm
```
Expected: **529 records**

### **Check Individuals**
```sql
SELECT COUNT(DISTINCT Individual_Id) as Unique_Individuals 
FROM Individual_Insights__dlm
```
Expected: **100 individuals**

### **Check Time Range**
```sql
SELECT 
    MIN(Event_Timestamp) as Oldest_Event,
    MAX(Event_Timestamp) as Latest_Event
FROM Individual_Insights__dlm
```
Expected: Last 90 days

---

## 🎉 Success!

Your Individual Insights object is now ready to power advanced personalization, predictive analytics, and behavioral targeting in Salesforce Data Cloud!

**Next Steps:**
1. Create segments using sentiment and purchase intent
2. Build calculated insights for real-time scores
3. Activate personalized campaigns based on lifestyle and events
4. Monitor trends over time for predictive modeling

---

## 📞 Support

For questions or issues:
- Check Salesforce Data Cloud documentation
- Review object field mappings
- Validate primary key constraints
- Test queries in Data Cloud Query Studio


