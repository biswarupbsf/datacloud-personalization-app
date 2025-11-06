# Data Cloud Contact Point Mapping Guide

## Overview

The **synthetic_engagement.csv** file now includes additional fields to enable mapping to Data Cloud's **ContactPointPhone** and **ContactPointOTT** (Over-The-Top) Data Model Objects (DMOs).

---

## 📞 ContactPointPhone DMO Mapping

ContactPointPhone represents phone contact information for individuals, including country codes and phone types.

### Field Mappings

| CSV Column | Data Cloud DMO Field | Data Type | Description | Example |
|------------|---------------------|-----------|-------------|---------|
| `Phone` | `ssot__TelephoneNumber__c` | Text | Full phone number with country code | +919154321430 |
| `Phone_Display` | `ssot__FormattedInternationalPhoneNumber__c` | Text | Human-readable format | +91 91543 21430 |
| `Country` | `ssot__Country__c` | Text | Country name | India, United States |
| `CountryCode` | `ssot__CountryIsoCode__c` | Text | ISO 3166-1 alpha-2 code | IN, US, GB, AU, CA, SG |
| `PhoneType` | `ssot__ContactPointPhoneType__c` | Picklist | Phone type | Mobile, Home, Work |
| `IsPrimaryPhone` | `ssot__IsPrimary__c` | Boolean | Primary contact flag | true, false |

### Sample Data

```csv
Phone,Phone_Display,Country,CountryCode,PhoneType,IsPrimaryPhone
+919154321430,+91 91543 21430,India,IN,Mobile,true
+917730660694,+91 77306 60694,United States,US,Home,false
```

### Data Cloud Upload Configuration

When creating a **Data Stream** for ContactPointPhone:

1. **Object Type**: ContactPointPhone DMO
2. **Primary Key**: Phone + Individual_Id (composite)
3. **Relationships**:
   - `Individual_Id` → `Individual.id` (Foreign Key)
4. **Field Type Mappings**:
   - Text: Phone, Phone_Display, Country, CountryCode, PhoneType
   - Boolean: IsPrimaryPhone

---

## 📱 ContactPointOTT DMO Mapping

ContactPointOTT (Over-The-Top) represents messaging app contact points and device information for individuals.

### Field Mappings

| CSV Column | Data Cloud DMO Field | Data Type | Description | Example |
|------------|---------------------|-----------|-------------|---------|
| `DeviceId` | `ssot__DeviceId__c` | Text | Unique device identifier | DEV_69735 |
| `MessagingPlatform` | `ssot__Platform__c` | Picklist | Messaging platform | WhatsApp, Telegram, Signal, WeChat |
| `DeviceType` | `ssot__DeviceType__c` | Picklist | Device OS/type | iOS, Android, Web |
| `AppVersion` | `ssot__ApplicationVersion__c` | Text | App version number | 2.23.1, 3.0.0 |
| `IsActiveDevice` | `ssot__IsActive__c` | Boolean | Active device flag | true, false |

### Sample Data

```csv
DeviceId,MessagingPlatform,DeviceType,AppVersion,IsActiveDevice
DEV_69735,WhatsApp,Android,2.23.1,true
DEV_71672,Signal,Web,3.0.0,true
DEV_13524,WeChat,iOS,2.24.1,false
```

### Data Cloud Upload Configuration

When creating a **Data Stream** for ContactPointOTT:

1. **Object Type**: ContactPointOTT DMO
2. **Primary Key**: DeviceId
3. **Relationships**:
   - `Individual_Id` → `Individual.id` (Foreign Key)
4. **Field Type Mappings**:
   - Text: DeviceId, MessagingPlatform, DeviceType, AppVersion
   - Boolean: IsActiveDevice

---

## 🔗 Relationship Configuration

After uploading the data streams, configure relationships in the **Data Model**:

### Individual → ContactPointPhone

```
Source Object: Individual_Engagement
Target Object: ContactPointPhone
Relationship Type: One-to-Many
Foreign Key: Individual_Id (in ContactPointPhone)
Related Field: id (in Individual_Engagement)
```

### Individual → ContactPointOTT

```
Source Object: Individual_Engagement
Target Object: ContactPointOTT
Relationship Type: One-to-Many
Foreign Key: Individual_Id (in ContactPointOTT)
Related Field: id (in Individual_Engagement)
```

---

## 📊 Complete Upload Process

### Step 1: Upload Individual Engagement

```
Data Streams → New → Upload CSV
Name: Individual_Engagement_Stream
File: synthetic_engagement.csv
Primary Key: id
Save & Activate
```

### Step 2: Create ContactPointPhone View (Optional)

If you want to create a separate ContactPointPhone object:

1. **Transform the Individual_Engagement data** to extract phone fields
2. **Map to ContactPointPhone DMO** fields
3. **Create relationship** back to Individual

### Step 3: Create ContactPointOTT View (Optional)

Similarly for OTT:

1. **Transform the Individual_Engagement data** to extract device/messaging fields
2. **Map to ContactPointOTT DMO** fields
3. **Create relationship** back to Individual

---

## 🔍 Verification Queries

After upload, run these queries in **Data Cloud Query Studio**:

### Check Phone Distribution by Country

```sql
SELECT 
    Country,
    CountryCode,
    COUNT(*) as Individual_Count,
    COUNT(DISTINCT PhoneType) as Phone_Types
FROM Individual_Engagement
GROUP BY Country, CountryCode
ORDER BY Individual_Count DESC;
```

### Check Messaging Platform Usage

```sql
SELECT 
    MessagingPlatform,
    DeviceType,
    COUNT(*) as User_Count,
    ROUND(AVG(CASE WHEN IsActiveDevice = 'true' THEN 100.0 ELSE 0.0 END), 2) as Active_Percentage
FROM Individual_Engagement
GROUP BY MessagingPlatform, DeviceType
ORDER BY User_Count DESC;
```

### Get Complete Contact Point Profile

```sql
SELECT 
    Name,
    Email,
    Phone,
    Country,
    CountryCode,
    PhoneType,
    DeviceId,
    MessagingPlatform,
    DeviceType,
    omnichannel_score
FROM Individual_Engagement
WHERE Email = 'bbanerjee@salesforce.com';
```

### Find High-Engagement WhatsApp Users

```sql
SELECT 
    Name,
    Email,
    Phone,
    Country,
    MessagingPlatform,
    DeviceType,
    omnichannel_score,
    whatsapp_reads
FROM Individual_Engagement
WHERE MessagingPlatform = 'WhatsApp'
  AND omnichannel_score >= 8
  AND IsActiveDevice = 'true'
ORDER BY omnichannel_score DESC
LIMIT 20;
```

---

## 📋 Field Summary

### Total Columns in synthetic_engagement.csv: **51**

#### Core Identity (3)
- id, Name, Email

#### Engagement Metrics (15)
- email_opens, email_clicks, sms_opens, whatsapp_reads, push_opens
- website_product_views, website_add_to_cart, total_order_value
- omnichannel_score, engagement_tier, fav_category, last_browsed, last_purchased
- data_source, last_engagement_date

#### Contact Point - Phone (6)
- Phone, Phone_Display
- **Country**, **CountryCode**, **PhoneType**, **IsPrimaryPhone**

#### Contact Point - OTT (5)
- **DeviceId**, **MessagingPlatform**, **DeviceType**, **AppVersion**, **IsActiveDevice**

#### Demographics (22)
- FirstName, LastName, Individual_FirstName, Individual_LastName, Individual_Name
- Individual_Email, Gender, Age, City, State, Postal_Code
- Account_Name, Loyalty_Status, Lifetime_Value, Preferred_Channel
- Last_Purchase_Date, Last_Purchase_Amount, Marketing_Consent
- Email_Consent, SMS_Consent, Phone_Consent, Push_Consent

---

## 🎯 Use Cases

### 1. Multi-Channel Personalization
Use phone country codes and messaging platforms to:
- Send localized content based on country
- Choose optimal messaging channel (WhatsApp vs others)
- Respect regional preferences

### 2. Device-Specific Campaigns
Target users based on:
- Device type (iOS vs Android)
- Active devices only
- Specific app versions for feature-based campaigns

### 3. Contact Preference Management
- Identify primary phone numbers for important communications
- Track messaging platform preferences
- Manage multi-device users

### 4. Geographic Segmentation
- Create country-specific segments
- Regional campaign targeting
- Compliance with regional regulations (GDPR, CCPA, etc.)

---

## 🚀 Next Steps

1. **Upload** `synthetic_engagement.csv` to Data Cloud
2. **Verify** field mappings in Data Model
3. **Create** relationships between objects
4. **Test** queries to ensure data integrity
5. **Build** segments using Contact Point fields
6. **Activate** campaigns with multi-channel targeting

---

## 📚 References

- [Data Cloud DMO Naming Standards](https://confluence.internal.salesforce.com/spaces/DOCTEAM/pages/1066848292/Data+Cloud+CX+DMO+Naming+Standards)
- [ContactPointPhone DMO Documentation](https://developer.salesforce.com/docs/data/data-cloud-ref/guide/c360dm-datamodelobjects.html)
- [Data Cloud Integration Guide](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started.htm&type=5)

---

**Updated:** November 1, 2025  
**Version:** 1.0  
**File Location:** `/Users/bbanerjee/.cursor/DC MCP/datacloud_app/`



