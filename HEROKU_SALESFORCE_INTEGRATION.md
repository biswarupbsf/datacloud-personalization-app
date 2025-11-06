# 🔗 Heroku + Salesforce Integration Guide

This guide covers how to connect your Heroku-deployed Data Cloud app with Salesforce using various integration methods.

---

## 🎯 Integration Options

### Option 1: **Direct API Connection** (Current Setup ✅)
Your app already uses `simple-salesforce` to connect via REST API. This works perfectly on Heroku!

### Option 2: **Heroku Connect** (Recommended for Production)
Syncs Salesforce data to Heroku Postgres in real-time.

### Option 3: **Salesforce Canvas**
Embed your Heroku app inside Salesforce UI.

### Option 4: **Heroku External Objects**
Access Heroku Postgres data from Salesforce.

---

## 📋 Option 1: Direct API Connection (Current Setup)

### Your App Already Works! ✅

Your current app uses Salesforce SOAP authentication and REST API. Here's how to configure it on Heroku:

### Step 1: Set Environment Variables on Heroku

```bash
# Basic Salesforce credentials
heroku config:set SF_USERNAME="your-username@salesforce.com"
heroku config:set SF_PASSWORD="your-password"
heroku config:set SF_SECURITY_TOKEN="your-security-token"

# For Data Cloud
heroku config:set SF_INSTANCE_URL="https://your-instance.salesforce.com"
```

### Step 2: Verify Configuration

```bash
# View all config vars
heroku config

# Test connection
heroku logs --tail
```

### Step 3: Update app.py for Environment Variables (Already Done! ✅)

Your app already reads from environment variables when they're available.

---

## 🔄 Option 2: Heroku Connect (Production-Grade Integration)

**Heroku Connect** syncs Salesforce data to a Heroku Postgres database in real-time.

### Benefits:
- ✅ Bi-directional sync with Salesforce
- ✅ No API limits (uses bulk API)
- ✅ Real-time or scheduled sync
- ✅ Works with large datasets
- ✅ Perfect for Data Cloud integration

### Setup Steps:

#### 1. Add Heroku Postgres

```bash
# Add Postgres database
heroku addons:create heroku-postgresql:mini

# Verify
heroku pg:info
```

#### 2. Add Heroku Connect

```bash
# Add Heroku Connect add-on
heroku addons:create herokuconnect:demo

# Open Heroku Connect dashboard
heroku addons:open herokuconnect
```

#### 3. Configure Heroku Connect

1. **Authenticate to Salesforce**
   - Click "Authorize" in Heroku Connect dashboard
   - Login with your Salesforce credentials
   - Grant permissions

2. **Select Objects to Sync**
   
   For your Data Cloud app, sync these objects:
   - ✅ **Individual** (People/Contacts)
   - ✅ **Campaign** (Marketing campaigns)
   - ✅ **CampaignMember** (Campaign membership)
   - ✅ **ContactPointEmail** (Email addresses)
   - ✅ **Order** (Purchase history)
   
   For Data Cloud-specific objects:
   - ✅ **UnifiedIndividual__dlm** (Data Cloud individuals)
   - ✅ **BU2_EmailEngagement__dlm** (Email engagement)
   - ✅ **Profile_Contact_and_Engagement__dlm** (Contact profiles)

3. **Configure Field Mappings**
   - Map Salesforce fields to Postgres columns
   - Choose sync direction (Salesforce → Heroku, or bi-directional)
   - Set sync frequency (real-time or scheduled)

4. **Start Sync**
   - Click "Start Sync"
   - Wait for initial data load

#### 4. Update Your App to Use Postgres

Install additional dependencies:

```bash
# Add to requirements.txt
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23
```

Update `app.py` to query Postgres instead of Salesforce API:

```python
import os
import psycopg2
from urllib.parse import urlparse

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Connect to Heroku Postgres"""
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn

# Example: Query synced Individual data
def get_individuals():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM salesforce.individual LIMIT 100")
    individuals = cur.fetchall()
    cur.close()
    conn.close()
    return individuals
```

### Benefits of Heroku Connect for Your App:

1. **No API Limits**
   - Sync millions of records
   - No 15,000 API calls/day limit

2. **Real-Time Data**
   - Changes in Salesforce appear in Heroku immediately
   - Changes in Heroku sync back to Salesforce

3. **Better Performance**
   - Query local Postgres instead of API calls
   - Faster dashboards and analytics

4. **Offline Capability**
   - App works even if Salesforce is down
   - Data cached in Postgres

---

## 🖼️ Option 3: Salesforce Canvas (Embed Heroku App in Salesforce)

**Salesforce Canvas** lets you embed your Heroku app directly inside Salesforce UI.

### Use Cases:
- Display your Data Cloud dashboards inside Salesforce
- Show AI Agent recommendations in Salesforce
- View analytics without leaving Salesforce

### Setup Steps:

#### 1. Create Connected App in Salesforce

1. Go to **Setup** → **App Manager** → **New Connected App**

2. **Basic Settings:**
   - Connected App Name: `Data Cloud Manager`
   - API Name: `Data_Cloud_Manager`
   - Contact Email: `your-email@salesforce.com`

3. **Canvas App Settings:**
   - ✅ Enable **Force.com Canvas**
   - Canvas App URL: `https://your-app-name.herokuapp.com`
   - Access Method: **Signed Request (POST)**
   - Locations: 
     - ✅ Visualforce Page
     - ✅ Lightning Component
     - ✅ Mobile Nav
     - ✅ Publisher

4. **OAuth Settings:**
   - ✅ Enable OAuth Settings
   - Callback URL: `https://your-app-name.herokuapp.com/oauth/callback`
   - Selected OAuth Scopes:
     - Access and manage your data (api)
     - Perform requests on your behalf at any time (refresh_token, offline_access)

5. **Save** and note the **Consumer Key** and **Consumer Secret**

#### 2. Update Your Heroku App

Add Canvas authentication to `app.py`:

```python
import base64
import hashlib
import hmac
import json
from flask import request

# Canvas consumer secret (set as env var)
CANVAS_CONSUMER_SECRET = os.environ.get('CANVAS_CONSUMER_SECRET')

@app.route('/canvas', methods=['POST'])
def canvas_handler():
    """Handle Salesforce Canvas signed request"""
    signed_request = request.form.get('signed_request')
    
    if not signed_request:
        return "No signed request", 400
    
    # Decode and verify signature
    encoded_sig, encoded_envelope = signed_request.split('.', 1)
    
    # Verify signature
    expected_sig = base64.urlsafe_b64encode(
        hmac.new(
            CANVAS_CONSUMER_SECRET.encode(),
            encoded_envelope.encode(),
            hashlib.sha256
        ).digest()
    )
    
    if encoded_sig.encode() != expected_sig.rstrip(b'='):
        return "Invalid signature", 403
    
    # Decode canvas request
    canvas_request = json.loads(
        base64.urlsafe_b64decode(encoded_envelope + '==')
    )
    
    # Extract Salesforce context
    sf_context = canvas_request.get('context', {})
    user = sf_context.get('user', {})
    
    # Render your app for Canvas
    return render_template('canvas_dashboard.html', 
                         user=user,
                         sf_context=sf_context)
```

#### 3. Set Environment Variables

```bash
heroku config:set CANVAS_CONSUMER_SECRET="your-consumer-secret"
```

#### 4. Add Canvas to Salesforce Page

Create a Visualforce page:

```html
<apex:page showHeader="false" sidebar="false">
    <apex:canvasApp applicationName="Data_Cloud_Manager" 
                    width="100%" 
                    height="900px"
                    scrolling="auto"/>
</apex:page>
```

Or use Lightning Component:

```javascript
<aura:component implements="force:appHostable,flexipage:availableForAllPageTypes">
    <force:canvasApp applicationName="Data_Cloud_Manager" 
                     width="100%" 
                     height="900px"/>
</aura:component>
```

---

## 🔐 Option 4: Heroku External Objects

**Heroku External Objects** let you access Heroku Postgres data from Salesforce using External Objects.

### Use Case:
- Query Heroku analytics data from Salesforce
- Use Heroku data in Salesforce reports
- Combine Salesforce + Heroku data in dashboards

### Setup:

#### 1. Install Heroku Connect

(Same as Option 2)

#### 2. Create External Data Source in Salesforce

1. Go to **Setup** → **External Data Sources** → **New**
2. Type: **OData 2.0**
3. URL: `https://your-app-name.herokuapp.com/odata/v2`
4. Authentication: **OAuth 2.0**

#### 3. Create External Objects

1. **Setup** → **External Objects** → **New**
2. Map to Heroku Postgres tables
3. Use in reports, dashboards, SOQL

---

## 🏗️ Recommended Architecture for Production

### For Your Data Cloud App:

```
┌─────────────────────────────────────────────────────────────┐
│                     Salesforce Data Cloud                    │
│  (Source: Individuals, Engagement, Orders, Insights)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Heroku Connect
                         │ (Real-time Sync)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Heroku Postgres Database                   │
│  • Individual records                                        │
│  • Engagement metrics (email, SMS, web)                     │
│  • Behavioral insights                                       │
│  • Segment definitions                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ SQLAlchemy ORM
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Flask App on Heroku (Your App!)                 │
│  • Analytics Dashboards                                      │
│  • AI Agent                                                  │
│  • Segment Builder                                           │
│  • Email Generator                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Embedded via Canvas
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               Salesforce Lightning Experience                │
│  (Your app embedded in Salesforce UI)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 Data Persistence Strategy

### Current Setup (File-Based):
```
Heroku Dyno Filesystem
├── data/
│   ├── segments.json
│   ├── synthetic_engagement.json
│   └── individual_insights.json
└── generated_emails/
    └── *.html

⚠️  Lost on dyno restart (every 24 hours)
```

### Recommended Setup (Database):
```
Heroku Postgres
├── segments (table)
├── individuals (table)
├── engagement_metrics (table)
├── insights (table)
└── generated_emails (table)

✅ Persistent across restarts
✅ Scalable to millions of records
✅ Real-time sync with Salesforce
```

---

## 🚀 Quick Start: Deploy with Heroku Connect

### Complete Setup (15 minutes):

```bash
# 1. Deploy your app
cd "/Users/bbanerjee/.cursor/DC MCP/datacloud_app"
./deploy_to_heroku.sh

# 2. Add Postgres
heroku addons:create heroku-postgresql:mini

# 3. Add Heroku Connect
heroku addons:create herokuconnect:demo

# 4. Open Heroku Connect dashboard
heroku addons:open herokuconnect

# 5. Authenticate to Salesforce (in browser)
# 6. Select objects to sync
# 7. Start sync

# 8. Test connection
heroku pg:psql
\dt salesforce.*
SELECT COUNT(*) FROM salesforce.individual;

# 9. Your app now has access to Salesforce data in Postgres! 🎉
```

---

## 📊 Cost Breakdown

### Heroku Connect Pricing:

- **Demo**: Free (100 records, good for testing)
- **Basic**: $10/month (10,000 records)
- **Professional**: $50/month (100,000 records)
- **Enterprise**: $400/month (Unlimited records)

### Total Monthly Cost:

**For Testing/Demo:**
```
Heroku Eco Dyno:        $5/month
Heroku Postgres (Mini): $5/month
Heroku Connect (Demo):  $0/month (free tier)
─────────────────────────────────
Total:                  $10/month
```

**For Production:**
```
Heroku Hobby Dyno:              $7/month
Heroku Postgres (Basic):        $9/month
Heroku Connect (Professional):  $50/month
─────────────────────────────────────────
Total:                          $66/month
```

---

## 🔧 Environment Variables Checklist

Set these on Heroku:

```bash
# Salesforce credentials
heroku config:set SF_USERNAME="your-username"
heroku config:set SF_PASSWORD="your-password"
heroku config:set SF_SECURITY_TOKEN="your-token"

# Salesforce instance
heroku config:set SF_INSTANCE_URL="https://your-instance.salesforce.com"

# Canvas (if using)
heroku config:set CANVAS_CONSUMER_SECRET="your-secret"

# Database (automatically set by Heroku)
# DATABASE_URL (auto-set when adding Postgres)

# App configuration
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set FLASK_ENV="production"
```

---

## ✅ Testing Your Integration

### 1. Test API Connection

```bash
heroku run python
>>> from simple_salesforce import Salesforce
>>> sf = Salesforce(username='...', password='...', security_token='...')
>>> sf.query("SELECT Id, Name FROM Individual LIMIT 5")
```

### 2. Test Heroku Connect

```bash
heroku pg:psql
SELECT * FROM salesforce.individual LIMIT 5;
```

### 3. Test Canvas

Visit your app in Salesforce and verify it loads correctly.

---

## 🎯 Next Steps

1. **Deploy to Heroku** (if not done):
   ```bash
   ./deploy_to_heroku.sh
   ```

2. **Choose Integration Method:**
   - Start with **Direct API** (already working!)
   - Add **Heroku Connect** for production scale
   - Add **Canvas** to embed in Salesforce UI

3. **Migrate to Postgres** (recommended):
   - Better performance
   - Data persistence
   - Real-time sync

4. **Monitor & Scale:**
   ```bash
   heroku logs --tail
   heroku pg:info
   heroku ps
   ```

---

## 📞 Support Resources

- **Heroku Dev Center**: https://devcenter.heroku.com/
- **Heroku Connect Docs**: https://devcenter.heroku.com/articles/heroku-connect
- **Salesforce Canvas Guide**: https://developer.salesforce.com/docs/atlas.en-us.platform_connect.meta/platform_connect/
- **Your Deployment Guide**: `HEROKU_DEPLOYMENT_GUIDE.md`

---

## 🎉 You're Ready!

Your Data Cloud app can now:
- ✅ Run on Heroku
- ✅ Connect to Salesforce via API
- ✅ Sync data with Heroku Connect
- ✅ Embed in Salesforce via Canvas
- ✅ Scale to millions of records

Deploy and start building! 🚀

