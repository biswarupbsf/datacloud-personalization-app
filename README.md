# 🌩️ Data Cloud Manager

A comprehensive web application for managing Salesforce Data Cloud. Create data, build relationships, segment audiences, and generate personalized email campaigns - all from a beautiful, easy-to-use interface.

## ✨ Features

### 🔐 Authentication
- Secure Salesforce login with username/password
- Optional security token support
- Session management

### 💾 Data Management
- **CRUD Operations**: Create, Read, Update, Delete records
- **Bulk Creation**: Generate multiple records at once
- **Multi-Object Support**: Individuals, Contacts, Accounts, Campaigns, Opportunities, and more
- **Real-time Data**: Direct integration with Salesforce API

### 🔗 Relationship Builder
- **Discover Relationships**: Automatically detect parent and child relationships
- **Visualize Connections**: See how objects relate to each other
- **Create Links**: Connect records across different objects
- **Relationship Graph**: Visual representation of object relationships

### 🎯 Segmentation Engine
- **Create Segments**: Filter records based on multiple criteria
- **Preview Results**: See segment members before saving
- **Sync to Campaigns**: Automatically create Salesforce Campaigns
- **Saved Segments**: Store and reuse segment configurations

### 📧 Email Campaign Generator
- **Personalized Templates**: VIP welcome emails with dynamic content
- **Engagement-Based**: Customize by engagement level (Exceptional, Outstanding, Excellent)
- **Unique Promo Codes**: Generate individual discount codes
- **Batch Sending**: Send to entire segments at once
- **Preview Emails**: See how emails look before sending

### 📊 Analytics Dashboard
- **Real-time Stats**: Track Individuals, Contacts, Campaigns, Opportunities
- **Segment Analytics**: Monitor segment performance
- **Email Metrics**: Open rates, click rates, engagement
- **Visual Reports**: Easy-to-understand charts and graphs

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Salesforce Data Cloud org access
- Salesforce username and password
- (Optional) Security token if IP not whitelisted

### Installation

1. **Navigate to the app directory:**
```bash
cd /Users/bbanerjee/.cursor/DC\ MCP/datacloud_app
```

2. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

3. **Run the application:**
```bash
python3 app.py
```

4. **Open your browser:**
Navigate to `http://localhost:5000`

## 📖 User Guide

### Step 1: Login

1. Open `http://localhost:5000`
2. Enter your Salesforce credentials:
   - **Username**: your.email@salesforce.com
   - **Password**: Your Salesforce password
   - **Security Token**: Leave blank if your IP is whitelisted
3. Click "Connect to Salesforce"

### Step 2: Create Data

1. Go to **Data Management** from the sidebar
2. Select an object (Individual, Contact, etc.)
3. Click "Create Records"
4. Enter the number of records to create
5. Records will be automatically generated with test data

**Example**: Create 100 Individuals
- Object: Individual
- Count: 100
- Template: Auto-generated (Test Person1, Test Person2, etc.)

### Step 3: Build Relationships

1. Go to **Relationship Builder**
2. Select an object to explore
3. View parent relationships (lookups)
4. View child relationships
5. Create connections between records

**Common Relationships**:
- Individual → Contact (via IndividualId)
- Contact → Campaign (via CampaignMember)
- Individual → ContactPointEmail (via ParentId)

### Step 4: Create Segments

1. Go to **Segments**
2. Click "Create Segment"
3. Fill in segment details:
   - **Name**: "VIP - Highly Engaged"
   - **Description**: "Top 10% engaged users"
   - **Base Object**: Individual
4. Add filters:
   - Field: Engagement Score
   - Operator: Greater Than
   - Value: 4
5. Click "Preview" to see results
6. Click "Create Segment" to save

### Step 5: Generate Personalized Emails

1. Go to **Email Campaigns**
2. Select a segment
3. Choose email template (VIP Welcome)
4. Click "Preview" to see sample emails
5. Click "Generate Emails" to create personalized emails
6. Review generated emails
7. Click "Send" to send to all segment members

### Step 6: Monitor Analytics

1. Go to **Analytics**
2. View segment statistics
3. Monitor email performance
4. Track engagement metrics

## 🎨 Email Personalization

The VIP Welcome email template includes:

- **Dynamic Greetings**: Based on recipient rank
- **Engagement Levels**: 
  - 🌟🌟🌟 EXCEPTIONAL (Score 7+)
  - 🌟🌟 OUTSTANDING (Score 5-6)
  - 🌟 EXCELLENT (Score 4)
- **Personal Stats**: Email opens, clicks, score, rank
- **Unique Promo Codes**: VIP01WELCOME, VIP02WELCOME, etc.
- **Custom Benefits**: VIP-only discounts, priority support
- **Beautiful Design**: Purple gradient header, gold VIP badge

## 🔧 Configuration

### Modifying Email Templates

Edit templates in: `templates/email_templates/vip_welcome.json`

```json
{
  "id": "vip_welcome",
  "name": "VIP Welcome Email",
  "subject_template": "🌟 {greeting}, {first_name}!",
  "html_template": "<!-- Your HTML here -->",
  "variables": ["greeting", "first_name", "full_name", ...]
}
```

### Adding Custom Objects

Objects are automatically loaded from your Salesforce org. To prioritize certain objects, edit `modules/data_manager.py`:

```python
common_objects = [
    'Individual', 'Contact', 'Account', 
    'YourCustomObject__c'  # Add your custom object
]
```

## 📁 Project Structure

```
datacloud_app/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── modules/
│   ├── salesforce_connector.py # Salesforce authentication
│   ├── data_manager.py         # Data CRUD operations
│   ├── relationship_builder.py # Relationship discovery
│   ├── segmentation_engine.py  # Segment creation/management
│   └── email_generator.py      # Email generation/sending
├── templates/
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard
│   ├── data_management.html   # Data CRUD interface
│   ├── relationships.html     # Relationship builder
│   ├── segments.html          # Segmentation interface
│   ├── emails.html            # Email campaign interface
│   ├── analytics.html         # Analytics dashboard
│   └── sidebar.html           # Navigation sidebar
├── static/
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── data_management.js # Data management JS
└── data/
    └── segments.json          # Saved segments (auto-generated)
```

## 🎯 Common Use Cases

### Use Case 1: VIP Email Campaign

**Goal**: Send personalized welcome emails to top 11 engaged users

1. Create 100 Individuals (Data Management)
2. Create ContactPointEmails for each (Relationships)
3. Simulate engagement data (or use real data)
4. Create segment: "Engagement Score > 4" (Segments)
5. Generate VIP emails (Email Campaigns)
6. Preview and send

**Result**: 11 personalized emails with unique promo codes and engagement stats

### Use Case 2: Lead Nurturing Campaign

**Goal**: Follow up with high-value leads

1. Query Leads with Annual Revenue > $100K
2. Create segment: "High Value Leads"
3. Generate follow-up emails
4. Track opens and clicks (Analytics)

### Use Case 3: Event Invitation

**Goal**: Invite engaged customers to webinar

1. Create segment: "Opened 3+ emails in last month"
2. Link to Campaign: "Q1 Webinar"
3. Generate event invitation emails
4. Track RSVPs

## 🔐 Security Notes

- **Never commit credentials** to version control
- Use environment variables for production
- Enable Two-Factor Authentication on Salesforce
- Whitelist your IP for easier access
- Rotate security tokens regularly

## 🐛 Troubleshooting

### "Connection Failed" on Login

**Solutions**:
1. Check username and password
2. Add security token if IP not whitelisted
3. Verify Salesforce org is accessible
4. Check network connectivity

### "No Records Found"

**Solutions**:
1. Create records using Data Management
2. Check object permissions
3. Verify SOQL query syntax
4. Check field-level security

### "Email Send Failed"

**Solutions**:
1. Verify email addresses are valid
2. Check Salesforce email sending limits
3. Ensure emailSimple API is available
4. Review Salesforce email deliverability settings

## 📚 API Documentation

### Authentication

**POST** `/login`
```json
{
  "username": "user@example.com",
  "password": "password",
  "security_token": "optional"
}
```

### Data Operations

**GET** `/api/data/objects` - List available objects

**GET** `/api/data/{object}/records` - Get records

**POST** `/api/data/{object}/create` - Create record

**POST** `/api/data/{object}/bulk-create` - Bulk create records

**PUT** `/api/data/{object}/{id}` - Update record

**DELETE** `/api/data/{object}/{id}` - Delete record

### Segments

**GET** `/api/segments/list` - List all segments

**POST** `/api/segments/create` - Create segment

**GET** `/api/segments/{id}/members` - Get segment members

**POST** `/api/segments/{id}/sync` - Sync to Salesforce Campaign

### Emails

**POST** `/api/emails/generate` - Generate personalized emails

**POST** `/api/emails/send` - Send emails

**POST** `/api/emails/preview` - Preview email

## 🚀 Next Steps

1. **Extend Email Templates**: Create templates for different use cases
2. **Add More Filters**: Enhance segmentation with advanced criteria
3. **Email A/B Testing**: Test different subject lines and content
4. **Scheduled Sends**: Schedule emails for optimal times
5. **Advanced Analytics**: Add conversion tracking and ROI metrics
6. **Mobile App**: Build iOS/Android companion apps
7. **Integration**: Connect with Marketing Cloud, Slack, etc.

## 📞 Support

For questions or issues:
- Email: bbanerjee@salesforce.com
- Salesforce Org: https://sftutor.lightning.force.com

## 📄 License

This application is for internal use within Salesforce Data Cloud environments.

---

**Built with ❤️ for Salesforce Data Cloud**

**Version**: 1.0.0  
**Last Updated**: October 30, 2025



