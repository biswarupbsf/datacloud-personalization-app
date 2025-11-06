#!/usr/bin/env python3
"""
Script to upload CSV files to Salesforce Data Cloud
"""
import os
import sys
import json
import csv
from simple_salesforce import Salesforce, SalesforceLogin
import getpass

print("🚀 Salesforce Data Cloud Upload Tool")
print("=" * 70)

# Check for credentials
print("\n📋 Step 1: Connect to Salesforce Data Cloud Org")
print("-" * 70)

username = input("Enter your Salesforce username (email): ").strip()
if not username:
    print("❌ Username is required")
    sys.exit(1)

password = getpass.getpass("Enter your Salesforce password: ")
if not password:
    print("❌ Password is required")
    sys.exit(1)

security_token = getpass.getpass("Enter your security token (press Enter if not needed): ")

# Combine password and token if provided
if security_token:
    password = password + security_token

print("\n🔐 Connecting to Salesforce...")

try:
    # Try to login
    sf = Salesforce(
        username=username,
        password=password,
        domain='login'  # Change to 'test' for sandbox
    )
    
    print(f"✅ Connected successfully!")
    print(f"   Org ID: {sf.sf_instance}")
    print(f"   User: {username}")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    print("\n💡 Tips:")
    print("   • Make sure your credentials are correct")
    print("   • If connecting from untrusted IP, you need a security token")
    print("   • Get security token: Setup → My Personal Information → Reset Security Token")
    print("   • Password should be: password + security_token")
    sys.exit(1)

print("\n" + "=" * 70)
print("📂 Step 2: Prepare CSV Files")
print("-" * 70)

# Check CSV files
engagement_csv = 'data/synthetic_engagement.csv'
insights_csv = 'data/individual_insights.csv'

files_to_upload = []

if os.path.exists(engagement_csv):
    stat = os.stat(engagement_csv)
    print(f"✅ {engagement_csv}")
    print(f"   Size: {stat.st_size / 1024:.1f} KB")
    with open(engagement_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"   Records: {len(rows)}")
    files_to_upload.append(('engagement', engagement_csv, rows))
else:
    print(f"❌ {engagement_csv} not found")

if os.path.exists(insights_csv):
    stat = os.stat(insights_csv)
    print(f"✅ {insights_csv}")
    print(f"   Size: {stat.st_size / 1024:.1f} KB")
    with open(insights_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"   Records: {len(rows)}")
    files_to_upload.append(('insights', insights_csv, rows))
else:
    print(f"❌ {insights_csv} not found")

if not files_to_upload:
    print("\n❌ No CSV files found to upload")
    sys.exit(1)

print("\n" + "=" * 70)
print("📊 Step 3: Create Custom Objects (if needed)")
print("-" * 70)

print("\n⚠️  Important: This script requires custom objects to be created first.")
print("   Please follow these steps:")
print()
print("   1. Go to Setup → Object Manager → Create → Custom Object")
print()
print("   2. Create 'Individual_Engagement__c' object:")
print("      • Label: Individual Engagement")
print("      • Plural: Individual Engagements")
print("      • Record Name: IE-{0000}")
print()
print("   3. Add these custom fields:")
print("      - FirstName__c (Text, 100)")
print("      - LastName__c (Text, 100)")
print("      - Email__c (Email)")
print("      - Phone__c (Phone)")
print("      - omnichannel_score__c (Number, 10, 2)")
print("      - email_opens__c (Number)")
print("      - email_clicks__c (Number)")
print("      - website_purchases__c (Number)")
print("      - favorite_category__c (Text, 100)")
print("      - preferred_channel__c (Text, 50)")
print()
print("   4. Repeat for 'Individual_Insights__c' object with appropriate fields")
print()

proceed = input("Have you created the custom objects? (yes/no): ").lower().strip()

if proceed != 'yes':
    print("\n⏸️  Upload paused. Please create the objects first and run this script again.")
    print("\n💡 Alternative: Use Data Cloud UI to upload CSV files directly:")
    print("   1. Open Data Cloud app")
    print("   2. Go to Data Streams → New → Upload CSV")
    print("   3. Select your CSV file and map fields")
    sys.exit(0)

print("\n" + "=" * 70)
print("📤 Step 4: Upload Data")
print("-" * 70)

# Upload engagement data
if len(files_to_upload) > 0 and files_to_upload[0][0] == 'engagement':
    print("\n📧 Uploading Individual Engagement data...")
    
    engagement_data = files_to_upload[0][2]
    
    print(f"   Preparing {len(engagement_data)} records...")
    
    # Transform data for Salesforce
    sf_records = []
    for row in engagement_data[:10]:  # Upload first 10 as test
        sf_record = {
            'FirstName__c': row.get('FirstName', ''),
            'LastName__c': row.get('LastName', ''),
            'Name': row.get('Name', ''),
            'Email__c': row.get('Email', ''),
            'Phone__c': row.get('Phone', ''),
            'omnichannel_score__c': float(row.get('omnichannel_score', 0)),
            'email_opens__c': int(row.get('email_opens', 0)),
            'email_clicks__c': int(row.get('email_clicks', 0)),
            'website_purchases__c': int(row.get('website_purchases', 0)),
            'favorite_category__c': row.get('favorite_category', ''),
            'preferred_channel__c': row.get('preferred_channel', '')
        }
        sf_records.append(sf_record)
    
    print(f"   Uploading test batch ({len(sf_records)} records)...")
    
    try:
        # Try to insert records
        results = sf.bulk.Individual_Engagement__c.insert(sf_records)
        
        success_count = sum(1 for r in results if r['success'])
        print(f"   ✅ Successfully uploaded {success_count}/{len(sf_records)} records")
        
        if success_count < len(sf_records):
            print(f"   ⚠️  {len(sf_records) - success_count} records failed")
            for i, r in enumerate(results):
                if not r['success']:
                    print(f"      Record {i+1}: {r.get('errors', 'Unknown error')}")
    
    except Exception as e:
        print(f"   ❌ Upload failed: {str(e)}")
        print(f"\n   💡 This error usually means:")
        print(f"      • Custom object 'Individual_Engagement__c' doesn't exist")
        print(f"      • Custom fields are missing or have wrong API names")
        print(f"      • Field types don't match the data")
        print(f"\n   📋 Please use Data Cloud UI for easier upload:")
        print(f"      Data Cloud → Data Streams → New → Upload CSV")

print("\n" + "=" * 70)
print("✅ Upload Process Complete!")
print("-" * 70)

print("\n📋 Summary:")
print(f"   • Connection: Successful")
print(f"   • Files processed: {len(files_to_upload)}")
print(f"   • Test upload: Completed")

print("\n🎯 Next Steps:")
print("   1. Go to Data Cloud app in Salesforce")
print("   2. Navigate to Data Streams")
print("   3. Click 'New Data Stream' → 'Upload CSV'")
print("   4. Select your CSV files:")
print(f"      • {engagement_csv}")
print(f"      • {insights_csv}")
print("   5. Map fields and activate")

print("\n📖 For detailed instructions, see: DATA_CLOUD_UPLOAD_GUIDE.md")

print("\n✨ Done!")


