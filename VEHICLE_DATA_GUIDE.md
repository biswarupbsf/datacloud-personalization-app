# Vehicle Data for Data Cloud - Complete Guide

## 📊 Overview

This guide documents the **Individual_Vehicles** data object created for Salesforce Data Cloud, containing comprehensive vehicle ownership and specification data linked to individuals.

---

## 🔍 Investigation Summary

### Salesforce Automotive Cloud Objects

Based on investigation of Data Cloud and Automotive Cloud documentation, the following vehicle-related objects were identified:

| Object | Purpose | Key Relationship |
|--------|---------|------------------|
| **Vehicle** | Individual vehicle instance | Links to Asset, VehicleDefinition |
| **VehicleDefinition** | Model/trim specifications | Links to Product2 |
| **Asset** | Asset tracking for vehicles | Links to Account (owner) |
| **Product2** | Product catalog entry | Base product information |
| **SerializedProduct** | Serialized tracking | Unique identifiers |

### Standard Fields in Automotive Cloud

The investigation revealed these comprehensive field categories:

- **Identity:** VIN, ChassisNumber, EngineNumber
- **Basic Info:** Make, Model, ModelYear, Trim
- **Specifications:** BodyType, FuelType, Transmission
- **Physical:** Color, DoorCount, Height, Length, Width
- **Engine:** CylinderCount, EngineCubicCapacity, FuelType
- **Registration:** RegistrationNumber, RegistrationRegionCode
- **Condition:** ConditionType, ManufacturedDate, Mileage
- **Valuation:** MarketPrice, AverageMarketValue, ResidualValue
- **Location:** LocationCity, LocationCountry, LocationPostalCode
- **Ownership:** AccountId (Owner), PurchaseDate
- **Telematics:** IsTelematicsServiceActive, DeviceId

---

## 📋 Individual_Vehicles Schema

### Complete Field List

| # | Field Name | Data Type | Description | Example |
|---|------------|-----------|-------------|---------|
| 1 | **VehicleId** | Text (PK) | Unique vehicle identifier | VEH_001_1 |
| 2 | **Individual_Id** | Text (FK) | Link to Individual owner | 0PKKX000000Tfjv4AC |
| 3 | **Individual_Name** | Text | Owner's name (for reference) | Biswarup Banerjee |
| 4 | **Individual_Email** | Email | Owner's email (for reference) | bbanerjee@salesforce.com |
| 5 | **VIN** | Text | Vehicle Identification Number (17 chars) | JFB27388074M0FHVY |
| 6 | **Make** | Text | Manufacturer | Maruti Suzuki, Hyundai, Tata |
| 7 | **Model** | Text | Vehicle model | Swift, Creta, Nexon |
| 8 | **ModelYear** | Number | Manufacturing year | 2015-2024 |
| 9 | **Trim** | Text | Trim level | Base, Mid, Top, Luxury, Sport |
| 10 | **RegistrationNumber** | Text | License plate | MH12AB1234 |
| 11 | **RegistrationState** | Text | Indian state code | MH, DL, KA, TN, etc. |
| 12 | **Color** | Text | Exterior color | White, Silver, Black, Red |
| 13 | **FuelType** | Picklist | Fuel type | Petrol, Diesel, CNG, Electric, Hybrid |
| 14 | **BodyType** | Picklist | Vehicle body type | Sedan, SUV, Hatchback, MPV |
| 15 | **Transmission** | Picklist | Transmission type | Manual, Automatic, AMT, CVT, DCT |
| 16 | **PurchaseDate** | Date | Date of purchase | 2020-03-15 |
| 17 | **Mileage** | Number | Current odometer (km) | 81,315 |
| 18 | **Condition** | Picklist | Vehicle condition | New, Used, Certified Pre-Owned |
| 19 | **MarketValue** | Currency | Current market value (₹) | 382,023 |
| 20 | **IsPrimaryVehicle** | Boolean | Primary vehicle flag | true, false |
| 21 | **TelematicsDeviceId** | Text | Connected car device ID | TELE_827011 |
| 22 | **IsTelematicsActive** | Boolean | Telematics service status | true, false |
| 23 | **InsuranceExpiryDate** | Date | Insurance expiration date | 2026-05-20 |
| 24 | **ServiceDueDate** | Date | Next service due date | 2026-02-03 |
| 25 | **ServiceDueMileage** | Number | Mileage for next service (km) | 90,000 |
| 26 | **data_source** | Text | Data source identifier | synthetic |

---

## 📊 Data Statistics

### Dataset Overview

- **Total Vehicles:** 114
- **Individuals with Vehicles:** 85 (85%)
- **Individuals without Vehicles:** 15 (15%)
- **Average Vehicles per Individual:** 1.14
- **Primary Vehicles:** 85
- **Secondary/Tertiary Vehicles:** 29

### Vehicle Distribution by Make

| Make | Count | Percentage |
|------|-------|------------|
| Toyota | 18 | 15.8% |
| MG | 14 | 12.3% |
| Maruti Suzuki | 13 | 11.4% |
| Tata | 13 | 11.4% |
| Renault | 12 | 10.5% |
| Hyundai | 12 | 10.5% |
| Kia | 11 | 9.6% |
| Volkswagen | 9 | 7.9% |
| Honda | 6 | 5.3% |
| Mahindra | 6 | 5.3% |

### Indian Automotive Market Representation

All makes and models are from vehicles commonly sold in India, including:

**Popular Brands:**
- **Maruti Suzuki:** Swift, Baleno, Wagon R, Alto, Ertiga, Brezza
- **Hyundai:** i20, Creta, Venue, Verna, Grand i10 Nios, Alcazar
- **Tata:** Nexon, Harrier, Safari, Punch, Altroz, Tiago
- **Mahindra:** XUV700, Scorpio, Thar, XUV300, Bolero
- **Toyota:** Fortuner, Innova Crysta, Urban Cruiser, Glanza
- **Kia:** Seltos, Sonet, Carens, EV6

---

## 🚀 Upload to Data Cloud

### Step 1: Create Data Stream

1. Navigate to **Data Cloud → Data Streams**
2. Click **New → Upload CSV**
3. **Name:** `Individual_Vehicles_Stream`
4. **Source File:** Select `individual_vehicles.csv` from Desktop
5. **Primary Key:** `VehicleId`

### Step 2: Field Mapping

Map CSV columns to Data Cloud fields:

#### Identity & Basic Info
```
VehicleId → ssot__VehicleId__c (Text, Primary Key)
Individual_Id → ssot__IndividualId__c (Text, Foreign Key)
VIN → ssot__VehicleIdentificationNumber__c (Text)
Make → ssot__Make__c (Text)
Model → ssot__Model__c (Text)
ModelYear → ssot__ModelYear__c (Number)
```

#### Registration & Ownership
```
RegistrationNumber → ssot__RegistrationNumber__c (Text)
RegistrationState → ssot__RegistrationState__c (Text)
PurchaseDate → ssot__PurchaseDate__c (Date)
IsPrimaryVehicle → ssot__IsPrimaryVehicle__c (Boolean)
```

#### Specifications
```
Trim → ssot__Trim__c (Text)
Color → ssot__Color__c (Text)
FuelType → ssot__FuelType__c (Picklist)
BodyType → ssot__BodyType__c (Picklist)
Transmission → ssot__Transmission__c (Picklist)
```

#### Condition & Value
```
Mileage → ssot__Mileage__c (Number)
Condition → ssot__Condition__c (Picklist)
MarketValue → ssot__MarketValue__c (Currency)
```

#### Service & Insurance
```
ServiceDueDate → ssot__ServiceDueDate__c (Date)
ServiceDueMileage → ssot__ServiceDueMileage__c (Number)
InsuranceExpiryDate → ssot__InsuranceExpiryDate__c (Date)
```

#### Telematics
```
TelematicsDeviceId → ssot__TelematicsDeviceId__c (Text)
IsTelematicsActive → ssot__IsTelematicsActive__c (Boolean)
```

### Step 3: Create Relationship

After uploading, create a relationship in **Data Model:**

```
Source Object: Individual_Vehicles
Target Object: Individual_Engagement
Relationship Type: Many-to-One
Foreign Key: Individual_Id (in Individual_Vehicles)
Related Field: id (in Individual_Engagement)
Relationship Name: Vehicles
```

---

## 🔍 Verification Queries

### Query 1: Check Total Vehicles

```sql
SELECT COUNT(*) as Total_Vehicles
FROM Individual_Vehicles;
-- Expected: 114
```

### Query 2: Vehicles by Make

```sql
SELECT 
    Make,
    COUNT(*) as Vehicle_Count,
    AVG(MarketValue) as Avg_Market_Value,
    AVG(Mileage) as Avg_Mileage
FROM Individual_Vehicles
GROUP BY Make
ORDER BY Vehicle_Count DESC;
```

### Query 3: High-Value Vehicle Owners

```sql
SELECT 
    v.Individual_Name,
    v.Individual_Email,
    v.Make,
    v.Model,
    v.ModelYear,
    v.MarketValue,
    e.omnichannel_score
FROM Individual_Vehicles v
JOIN Individual_Engagement e ON v.Individual_Id = e.id
WHERE v.MarketValue > 1000000
ORDER BY v.MarketValue DESC;
```

### Query 4: Service Due Soon

```sql
SELECT 
    Individual_Name,
    Make,
    Model,
    RegistrationNumber,
    Mileage,
    ServiceDueMileage,
    (ServiceDueMileage - Mileage) as Km_Until_Service,
    ServiceDueDate
FROM Individual_Vehicles
WHERE ServiceDueDate <= CURRENT_DATE + INTERVAL '30' DAY
ORDER BY ServiceDueDate;
```

### Query 5: Insurance Expiring Soon

```sql
SELECT 
    Individual_Name,
    Individual_Email,
    Make,
    Model,
    RegistrationNumber,
    InsuranceExpiryDate,
    DATEDIFF(day, CURRENT_DATE, InsuranceExpiryDate) as Days_Until_Expiry
FROM Individual_Vehicles
WHERE InsuranceExpiryDate <= CURRENT_DATE + INTERVAL '60' DAY
ORDER BY InsuranceExpiryDate;
```

### Query 6: Connected Cars Analysis

```sql
SELECT 
    COUNT(CASE WHEN IsTelematicsActive = 'true' THEN 1 END) as Connected_Vehicles,
    COUNT(CASE WHEN IsTelematicsActive = 'false' THEN 1 END) as Non_Connected_Vehicles,
    ROUND(100.0 * COUNT(CASE WHEN IsTelematicsActive = 'true' THEN 1 END) / COUNT(*), 2) as Connected_Percentage
FROM Individual_Vehicles;
```

### Query 7: Multi-Vehicle Owners

```sql
SELECT 
    Individual_Id,
    Individual_Name,
    COUNT(*) as Vehicle_Count,
    STRING_AGG(Make + ' ' + Model, ', ') as Vehicles
FROM Individual_Vehicles
GROUP BY Individual_Id, Individual_Name
HAVING COUNT(*) > 1
ORDER BY Vehicle_Count DESC;
```

### Query 8: Biswarup's Vehicle Profile

```sql
SELECT 
    v.*,
    e.omnichannel_score,
    e.email_opens,
    e.Phone,
    e.Country
FROM Individual_Vehicles v
JOIN Individual_Engagement e ON v.Individual_Id = e.id
WHERE v.Individual_Email = 'bbanerjee@salesforce.com';
```

---

## 🎯 Use Cases

### 1. Service Reminder Campaigns

**Target:** Vehicles with service due in next 30 days

```sql
SELECT 
    Individual_Email,
    Make,
    Model,
    ServiceDueDate,
    ServiceDueMileage
FROM Individual_Vehicles
WHERE ServiceDueDate BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
  AND IsPrimaryVehicle = 'true';
```

**Action:** Send personalized service reminder emails with:
- Vehicle details
- Service center locations
- Online booking link
- Special service offers

### 2. Insurance Renewal Campaign

**Target:** Vehicles with insurance expiring in 60 days

```sql
SELECT 
    v.Individual_Name,
    v.Individual_Email,
    v.Make,
    v.Model,
    v.InsuranceExpiryDate,
    v.MarketValue,
    e.Phone,
    e.Country
FROM Individual_Vehicles v
JOIN Individual_Engagement e ON v.Individual_Id = e.id
WHERE v.InsuranceExpiryDate BETWEEN CURRENT_DATE AND CURRENT_DATE + 60
ORDER BY v.InsuranceExpiryDate;
```

**Action:** Multi-channel outreach (Email + SMS + WhatsApp) with:
- Insurance renewal reminders
- Competitive quotes
- Online renewal options
- Add-on coverage options

### 3. Vehicle Upgrade Targeting

**Target:** Older, high-mileage vehicles for upgrade offers

```sql
SELECT 
    v.Individual_Name,
    v.Individual_Email,
    v.Make,
    v.Model,
    v.ModelYear,
    v.Mileage,
    v.MarketValue,
    e.omnichannel_score,
    e.Purchase_Intent
FROM Individual_Vehicles v
JOIN Individual_Engagement e ON v.Individual_Id = e.id
WHERE v.ModelYear < 2020
  AND v.Mileage > 80000
  AND e.omnichannel_score >= 7
ORDER BY e.omnichannel_score DESC, v.Mileage DESC;
```

**Action:** Personalized vehicle upgrade campaigns with:
- Trade-in value estimates
- New model recommendations
- Finance options
- Test drive bookings

### 4. Connected Car Services

**Target:** Non-connected vehicles for telematics upsell

```sql
SELECT 
    v.Individual_Name,
    v.Individual_Email,
    v.Make,
    v.Model,
    v.ModelYear,
    e.omnichannel_score,
    e.DeviceType
FROM Individual_Vehicles v
JOIN Individual_Engagement e ON v.Individual_Id = e.id
WHERE v.IsTelematicsActive = 'false'
  AND v.ModelYear >= 2020
  AND e.omnichannel_score >= 6
ORDER BY e.omnichannel_score DESC;
```

**Action:** Connected car feature campaigns with:
- Real-time vehicle tracking
- Remote diagnostics
- Theft protection
- Usage analytics

### 5. Premium Customer VIP Treatment

**Target:** High-value vehicle owners with high engagement

```sql
SELECT 
    v.Individual_Name,
    v.Individual_Email,
    v.Make,
    v.Model,
    v.MarketValue,
    e.omnichannel_score,
    e.Lifetime_Value,
    i.Purchase_Intent,
    i.Lifestyle_Quotient
FROM Individual_Vehicles v
JOIN Individual_Engagement e ON v.Individual_Id = e.id
LEFT JOIN Individual_Insights i ON v.Individual_Id = i.Individual_Id
WHERE v.MarketValue > 1500000
  AND e.omnichannel_score >= 8
ORDER BY v.MarketValue DESC, e.omnichannel_score DESC;
```

**Action:** VIP concierge services:
- Priority service appointments
- Complimentary vehicle pickup/drop
- Exclusive new model previews
- Premium lounge access

### 6. Geographic/Regional Campaigns

**Target:** Vehicles registered in specific states

```sql
SELECT 
    v.RegistrationState,
    COUNT(*) as Vehicle_Count,
    AVG(v.MarketValue) as Avg_Market_Value,
    COUNT(CASE WHEN v.IsTelematicsActive = 'true' THEN 1 END) as Connected_Count
FROM Individual_Vehicles v
GROUP BY v.RegistrationState
ORDER BY Vehicle_Count DESC;
```

**Action:** State-specific campaigns for:
- Regional service center promotions
- State-specific insurance offers
- Local dealer events
- Regional festivals/offers

---

## 📦 File Locations

### On Desktop (Ready for Upload)

1. **individual_vehicles.csv** (27 KB)
   - 114 vehicle records
   - 26 columns
   - Ready for Data Cloud upload

2. **synthetic_engagement.csv** (59 KB)
   - 100 individuals with Contact Point fields
   - Links to vehicles via Individual_Id

3. **individual_insights.csv** (135 KB)
   - 529 behavioral insights
   - Links to individuals and their vehicles

### In Application

- `data/individual_vehicles.csv` - Source CSV
- `data/individual_vehicles.json` - JSON format for app

---

## 🔗 Data Relationships

```
Individual_Engagement (1)
    ├─── Individual_Vehicles (1..3)
    │       └─── VehicleId (PK)
    │       └─── Individual_Id (FK)
    │
    ├─── Individual_Insights (1..N)
    │       └─── Individual_Id (FK)
    │
    └─── ContactPointPhone (1)
    └─── ContactPointOTT (1)
```

---

## ✨ Integration with Existing Data

The vehicle data seamlessly integrates with existing data objects:

### Individual Engagement
- Link via `Individual_Id`
- Use `omnichannel_score` to target high-engagement vehicle owners
- Use `Purchase_Intent` for upgrade campaigns

### Individual Insights
- Link via `Individual_Id`
- Use `Purchase_Intent` to identify ready-to-buy customers
- Use `Lifestyle_Quotient` (traveller, careerist) for targeting
- Use `Favourite_Brand` for brand-specific campaigns

### Contact Point Data
- Use `Phone`, `Email`, `MessagingPlatform` for multi-channel outreach
- Use `Country`, `CountryCode` for regional campaigns
- Use `DeviceType` for mobile app promotions

---

## 📊 Sample Records

### Biswarup Banerjee's Vehicle

```
VehicleId: VEH_001_1
Owner: Biswarup Banerjee (bbanerjee@salesforce.com)
Vehicle: Maruti Suzuki Baleno (2016)
VIN: JFB27388074M0FHVY
Registration: RJ03CZ3324 (Rajasthan)
Color: White | Fuel: Petrol | Transmission: Manual
Mileage: 81,315 km
Market Value: ₹382,023
Service Due: 2026-02-03 @ 90,000 km
Insurance Expiry: 2026-05-15
Connected: Yes (TELE_827011)
```

---

## 🚀 Ready to Upload!

All three data files are ready on your Desktop:

1. ✅ **synthetic_engagement.csv** - Individuals with Contact Points
2. ✅ **individual_insights.csv** - Behavioral Insights
3. ✅ **individual_vehicles.csv** - Vehicle Ownership (NEW!)

---

**Document Version:** 1.0  
**Last Updated:** November 1, 2025  
**Location:** `/Users/bbanerjee/.cursor/DC MCP/datacloud_app/`



