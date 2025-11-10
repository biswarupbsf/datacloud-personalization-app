#!/usr/bin/env python3
"""
Discover Email and Website Engagement Objects in Data Cloud
"""

from simple_salesforce import Salesforce
import requests
from xml.etree import ElementTree as ET

# Connection details
USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"

print("="*80)
print("DISCOVERING DATA CLOUD ENGAGEMENT OBJECTS")
print("="*80)

# Connect using SOAP
soap_url = 'https://login.salesforce.com/services/Soap/u/59.0'
soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                  xmlns:urn="urn:partner.soap.sforce.com">
  <soapenv:Body>
    <urn:login>
      <urn:username>{USERNAME}</urn:username>
      <urn:password>{PASSWORD}</urn:password>
    </urn:login>
  </soapenv:Body>
</soapenv:Envelope>"""

headers = {'Content-Type': 'text/xml; charset=UTF-8', 'SOAPAction': 'login'}
response = requests.post(soap_url, data=soap_body, headers=headers)

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    exit(1)

root = ET.fromstring(response.text)
ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/', 'urn': 'urn:partner.soap.sforce.com'}
session_id = root.find('.//urn:sessionId', ns).text
server_url = root.find('.//urn:serverUrl', ns).text
instance_url = '/'.join(server_url.split('/')[:3])

sf = Salesforce(instance_url=instance_url, session_id=session_id)
print(f"✅ Connected to {instance_url}\n")

# Get all objects
print("Fetching all objects...")
describe_global = sf.describe()

# Filter for engagement-related objects
engagement_objects = []
website_objects = []
email_objects = []

for obj in describe_global['sobjects']:
    obj_name = obj['name']
    obj_label = obj['label']
    
    # Look for email engagement
    if any(keyword in obj_name.lower() or keyword in obj_label.lower() 
           for keyword in ['email', 'engagement', 'click', 'open', 'bounce']):
        email_objects.append({
            'name': obj_name,
            'label': obj_label,
            'custom': obj['custom']
        })
    
    # Look for website engagement
    if any(keyword in obj_name.lower() or keyword in obj_label.lower() 
           for keyword in ['web', 'product', 'cart', 'browse', 'commerce', 'order']):
        website_objects.append({
            'name': obj_name,
            'label': obj_label,
            'custom': obj['custom']
        })

print("\n" + "="*80)
print("📧 EMAIL ENGAGEMENT OBJECTS")
print("="*80)

if email_objects:
    for obj in email_objects[:20]:  # Show first 20
        marker = "🔷" if obj['custom'] else "⚙️"
        print(f"{marker} {obj['name']} - {obj['label']}")
        
        # Try to get a count
        try:
            count_query = f"SELECT COUNT() FROM {obj['name']}"
            result = sf.query(count_query)
            print(f"   └─ {result['totalSize']} records")
        except:
            print(f"   └─ (Unable to query)")
else:
    print("❌ No email engagement objects found")

print("\n" + "="*80)
print("🌐 WEBSITE/COMMERCE ENGAGEMENT OBJECTS")
print("="*80)

if website_objects:
    for obj in website_objects[:20]:  # Show first 20
        marker = "🔷" if obj['custom'] else "⚙️"
        print(f"{marker} {obj['name']} - {obj['label']}")
        
        # Try to get a count
        try:
            count_query = f"SELECT COUNT() FROM {obj['name']}"
            result = sf.query(count_query)
            print(f"   └─ {result['totalSize']} records")
        except:
            print(f"   └─ (Unable to query)")
else:
    print("❌ No website/commerce objects found")

# Check for specific Data Cloud objects
print("\n" + "="*80)
print("🔍 CHECKING SPECIFIC DATA CLOUD OBJECTS")
print("="*80)

data_cloud_objects = [
    'IndividualEmailResult',
    'EngagementChannelActionHistory',
    'EngagementInteraction',
    'ContactPointEmail',
    'ListEmail',
    'WebEngagement',
    'ProductBrowsed',
    'CartEvent',
    'Order',
    'OrderItem',
    'Asset'
]

for obj_name in data_cloud_objects:
    try:
        # Try to describe the object
        desc = sf.__getattr__(obj_name).describe()
        
        # Get count
        count_query = f"SELECT COUNT() FROM {obj_name}"
        result = sf.query(count_query)
        
        print(f"✅ {obj_name}: {result['totalSize']} records")
        
        # Show some fields
        field_names = [f['name'] for f in desc['fields'][:10]]
        print(f"   Fields: {', '.join(field_names)}")
        
    except Exception as e:
        print(f"❌ {obj_name}: Not available ({str(e)[:50]})")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

print("\nBased on what's available, I'll create scripts to:")
print("1. Pull real email engagement data (opens, clicks, bounces)")
print("2. Pull website/commerce data (product views, cart events, purchases)")
print("3. Calculate engagement scores from actual data")
print("4. Link everything to Individual records")





