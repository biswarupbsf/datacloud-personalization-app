#!/usr/bin/env python3
"""
Discover SMS and WhatsApp Message Engagement in Data Cloud
"""

from simple_salesforce import Salesforce
import requests
from xml.etree import ElementTree as ET

# Connection details
USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"

print("="*80)
print("DISCOVERING SMS/WHATSAPP MESSAGE ENGAGEMENT OBJECTS")
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
print("Searching for message engagement objects...")
describe_global = sf.describe()

# Filter for message/SMS/WhatsApp related objects
message_objects = []
sms_objects = []
whatsapp_objects = []

for obj in describe_global['sobjects']:
    obj_name = obj['name']
    obj_label = obj['label']
    
    name_lower = obj_name.lower()
    label_lower = obj_label.lower()
    
    # Look for message engagement
    if any(keyword in name_lower or keyword in label_lower 
           for keyword in ['message', 'sms', 'whatsapp', 'push', 'mobileconnect', 'mobilepush']):
        
        obj_info = {
            'name': obj_name,
            'label': obj_label,
            'custom': obj['custom']
        }
        
        # Categorize
        if 'sms' in name_lower or 'sms' in label_lower:
            sms_objects.append(obj_info)
        elif 'whatsapp' in name_lower or 'whatsapp' in label_lower:
            whatsapp_objects.append(obj_info)
        else:
            message_objects.append(obj_info)

print("\n" + "="*80)
print("📱 SMS ENGAGEMENT OBJECTS")
print("="*80)

if sms_objects:
    for obj in sms_objects[:20]:
        marker = "🔷" if obj['custom'] else "⚙️"
        print(f"{marker} {obj['name']} - {obj['label']}")
        
        # Try to get a count
        try:
            count_query = f"SELECT COUNT() FROM {obj['name']}"
            result = sf.query(count_query)
            print(f"   └─ {result['totalSize']:,} records")
        except Exception as e:
            print(f"   └─ (Unable to query: {str(e)[:50]})")
else:
    print("❌ No SMS engagement objects found")

print("\n" + "="*80)
print("💬 WHATSAPP ENGAGEMENT OBJECTS")
print("="*80)

if whatsapp_objects:
    for obj in whatsapp_objects[:20]:
        marker = "🔷" if obj['custom'] else "⚙️"
        print(f"{marker} {obj['name']} - {obj['label']}")
        
        # Try to get a count
        try:
            count_query = f"SELECT COUNT() FROM {obj['name']}"
            result = sf.query(count_query)
            print(f"   └─ {result['totalSize']:,} records")
        except:
            print(f"   └─ (Unable to query)")
else:
    print("❌ No WhatsApp engagement objects found")

print("\n" + "="*80)
print("📲 OTHER MESSAGE ENGAGEMENT OBJECTS")
print("="*80)

if message_objects:
    for obj in message_objects[:20]:
        marker = "🔷" if obj['custom'] else "⚙️"
        print(f"{marker} {obj['name']} - {obj['label']}")
        
        # Try to get a count
        try:
            count_query = f"SELECT COUNT() FROM {obj['name']}"
            result = sf.query(count_query)
            print(f"   └─ {result['totalSize']:,} records")
        except:
            print(f"   └─ (Unable to query)")
else:
    print("❌ No other message engagement objects found")

# Check specific known message engagement objects
print("\n" + "="*80)
print("🔍 CHECKING SPECIFIC MESSAGE ENGAGEMENT OBJECTS")
print("="*80)

message_engagement_objects = [
    'BU2_MessageEngagement__dlm',
    'MessageEngagement__dlm',
    'SMSEngagement__dlm',
    'WhatsAppEngagement__dlm',
    'MobileConnectEngagement__dlm',
    'BU2_DeviceApplicationEngagement__dlm',
    'BU2_EinsteinPushEngagementScores__dlm'
]

found_any = False

for obj_name in message_engagement_objects:
    try:
        # Try to describe the object
        desc = sf.__getattr__(obj_name).describe()
        
        # Get count
        count_query = f"SELECT COUNT() FROM {obj_name}"
        result = sf.query(count_query)
        
        print(f"✅ {obj_name}: {result['totalSize']:,} records")
        
        # Show some fields
        field_names = [f['name'] for f in desc['fields'][:15]]
        print(f"   Fields: {', '.join(field_names)}")
        
        # Try to get a sample record
        if result['totalSize'] > 0:
            try:
                sample_query = f"SELECT {', '.join(field_names[:10])} FROM {obj_name} LIMIT 1"
                sample = sf.query(sample_query)['records'][0]
                print(f"   Sample record fields: {list(sample.keys())[:10]}")
            except:
                pass
        
        found_any = True
        print()
        
    except Exception as e:
        print(f"❌ {obj_name}: Not available")

print("\n" + "="*80)
print("SUMMARY & RECOMMENDATIONS")
print("="*80)

if found_any:
    print("\n✅ Message engagement data found in your org!")
    print("\nI'll create a script to:")
    print("1. Pull real message engagement data")
    print("2. Link it to Individuals")
    print("3. Calculate SMS/WhatsApp engagement scores")
else:
    print("\n⚠️  No message engagement data found in your org.")
    print("\n💡 I'll create synthetic SMS/WhatsApp engagement data:")
    print("1. SMS opens, clicks, bounces, opt-outs")
    print("2. WhatsApp opens, clicks, replies")
    print("3. Combined message engagement scores")
    print("4. Integration with existing email + website engagement")



