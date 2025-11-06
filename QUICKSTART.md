# 🚀 Quick Start Guide

Get up and running with Data Cloud Manager in 3 minutes!

## ⚡ Super Quick Start

```bash
cd /Users/bbanerjee/.cursor/DC\ MCP/datacloud_app
./start.sh
```

Then open: **http://localhost:5000**

## 📝 Step-by-Step Setup

### 1. Install Dependencies (30 seconds)

```bash
cd /Users/bbanerjee/.cursor/DC\ MCP/datacloud_app
pip3 install -r requirements.txt
```

### 2. Start the Server (5 seconds)

```bash
python3 app.py
```

You should see:
```
================================================================================
DATA CLOUD MANAGEMENT APPLICATION
================================================================================

🚀 Starting server...
📍 URL: http://localhost:5000
📖 API Docs: http://localhost:5000/api/docs

================================================================================
 * Running on http://0.0.0.0:5000
```

### 3. Login (1 minute)

1. Open browser: **http://localhost:5000**
2. Enter credentials:
   - Username: `biswarupb@salesforce.com`
   - Password: `SFTut0r25`
   - Security Token: *(leave blank)*
3. Click **"Connect to Salesforce"**

✅ You're in!

## 🎯 Quick Demo Workflow

### Create Your First VIP Email Campaign (5 minutes)

#### Step 1: Create Test Data
1. Go to **Data Management** (sidebar)
2. Select **"Individual"** from dropdown
3. Click **"+ Create Records"**
4. Enter **100** and click OK
5. Wait ~10 seconds for creation

**Result**: 100 test Individuals created

#### Step 2: Create Email Contacts
1. Stay in **Data Management**
2. Select **"ContactPointEmail"** from dropdown
3. View created contacts (auto-linked to Individuals)

#### Step 3: Create VIP Segment
1. Go to **Segments** (sidebar)
2. Fill in form:
   - Name: `VIP - Top Engaged`
   - Description: `Highly engaged users`
   - Base Object: `Individual`
3. Add a filter (any criteria)
4. Click **"Create Segment"**

**Result**: Segment with filtered members

#### Step 4: Generate VIP Emails
1. Go to **Email Campaigns** (sidebar)
2. Select your segment: `VIP - Top Engaged`
3. Template: `VIP Welcome Email`
4. Click **"Generate Emails"**

**Result**: Personalized emails for each member!

#### Step 5: Review & Send
1. Click **"Preview"** to see sample emails
2. Review personalization (names, stats, promo codes)
3. Click **"Send"** to email all members

**Result**: VIP welcome emails sent! 🎉

## 🎨 What You Get

### Beautiful Features:
- ✅ **Dashboard** with real-time stats
- ✅ **Data Management** for all Salesforce objects
- ✅ **Relationship Builder** to connect records
- ✅ **Segmentation Engine** with custom filters
- ✅ **Email Generator** with VIP templates
- ✅ **Analytics** dashboard

### Personalized Emails Include:
- 🌟 Engagement-based greetings (Exceptional/Outstanding/Excellent)
- 📊 Personal stats (opens, clicks, score, rank)
- 🎁 Unique promo codes (VIP01WELCOME, VIP02WELCOME...)
- 💜 Beautiful purple gradient design
- 🏆 Gold VIP badges

## 🔥 Power User Tips

### Bulk Create Records
```bash
# In Data Management:
1. Select object
2. Click "+ Create Records"
3. Enter count: 100, 500, 1000
4. Auto-generated with smart defaults
```

### Custom Filters
```bash
# In Segments:
Field: Engagement Score
Operator: Greater Than
Value: 4
```

### Preview Before Sending
```bash
# Always preview first:
1. Generate emails
2. Click "Preview"
3. Check personalization
4. Then send
```

## 🐛 Troubleshooting

### "Connection Failed"
```bash
# Solutions:
1. Check credentials
2. Try adding security token
3. Verify org access
```

### "No Records Found"
```bash
# Solutions:
1. Create records first (Data Management)
2. Check object permissions
```

### Port Already in Use
```bash
# Kill process on port 5000:
lsof -ti:5000 | xargs kill -9

# Or change port in app.py:
app.run(port=5001)
```

## 📱 Access from Other Devices

The app runs on `0.0.0.0:5000`, so you can access it from:
- **Local**: http://localhost:5000
- **Network**: http://YOUR_IP:5000

Find your IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

## 🎓 Learn More

- **Full Documentation**: See `README.md`
- **API Reference**: Check `app.py` for all endpoints
- **Custom Templates**: Edit `modules/email_generator.py`

## 💡 Example Workflows

### Workflow 1: Event Invitation
```
1. Create segment: "Opened 3+ emails"
2. Generate event invite emails
3. Track RSVPs in Analytics
```

### Workflow 2: Lead Nurturing
```
1. Query high-value leads
2. Create "High Value" segment
3. Send follow-up campaign
4. Monitor conversions
```

### Workflow 3: Re-engagement
```
1. Segment: "No opens in 30 days"
2. Generate re-engagement emails
3. Track response rate
4. Remove unresponsive
```

## 🎉 You're Ready!

You now have a full-featured Data Cloud management system.

**Next Steps**:
1. Explore all features
2. Create your own segments
3. Design custom email templates
4. Monitor analytics

**Questions?** Check the README.md for detailed documentation.

---

**Happy Data Cloud Managing!** 🌩️✨


