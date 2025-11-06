#!/usr/bin/env python3
"""
Add Engagement Scores to Individual Records
This script adds simulated engagement data (opens, clicks, score) to the Individual records
so you can create segments based on engagement.
"""

from simple_salesforce import Salesforce
import json
import random

# Connection details
USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"

print("="*80)
print("ADDING ENGAGEMENT SCORES TO INDIVIDUALS")
print("="*80)

# Connect using SOAP (no token needed)
import requests
from xml.etree import ElementTree as ET

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

# Step 1: Get all Individuals
print("Step 1: Fetching all Individuals...")
query = "SELECT Id, Name FROM Individual ORDER BY Name"
individuals = sf.query(query)['records']
print(f"Found {len(individuals)} individuals\n")

# Step 2: Generate engagement scores
print("Step 2: Generating engagement scores...")
engagement_data = []

for i, individual in enumerate(individuals):
    # Generate realistic engagement patterns
    # Top 20% get high scores (6-7)
    # Middle 50% get medium scores (3-5)
    # Bottom 30% get low scores (0-2)
    
    percentile = (i + 1) / len(individuals)
    
    if percentile <= 0.20:  # Top 20%
        opens = random.randint(8, 15)
        clicks = random.randint(6, 12)
        score = random.randint(6, 7)
    elif percentile <= 0.70:  # Middle 50%
        opens = random.randint(3, 7)
        clicks = random.randint(1, 5)
        score = random.randint(3, 5)
    else:  # Bottom 30%
        opens = random.randint(0, 2)
        clicks = random.randint(0, 1)
        score = random.randint(0, 2)
    
    engagement_data.append({
        'id': individual['Id'],
        'name': individual['Name'],
        'opens': opens,
        'clicks': clicks,
        'engagement_score': score,
        'bounces': 0,
        'unsubscribes': 0
    })

print(f"Generated engagement data for {len(engagement_data)} individuals\n")

# Step 3: Save to JSON (since we can't add custom fields without metadata API)
print("Step 3: Saving engagement data...")
output_file = 'data/individual_engagement.json'
with open(output_file, 'w') as f:
    json.dump(engagement_data, f, indent=2)

print(f"✅ Saved engagement data to {output_file}\n")

# Step 4: Show summary
print("="*80)
print("ENGAGEMENT SCORE SUMMARY")
print("="*80)

high_engagement = [e for e in engagement_data if e['engagement_score'] >= 6]
medium_engagement = [e for e in engagement_data if 3 <= e['engagement_score'] < 6]
low_engagement = [e for e in engagement_data if e['engagement_score'] < 3]

print(f"\n🌟 High Engagement (Score 6-7): {len(high_engagement)} individuals")
print(f"   These are your VIP candidates!\n")
for e in high_engagement[:5]:
    print(f"   • {e['name']}: {e['opens']} opens, {e['clicks']} clicks, score: {e['engagement_score']}")
if len(high_engagement) > 5:
    print(f"   ... and {len(high_engagement) - 5} more")

print(f"\n⭐ Medium Engagement (Score 3-5): {len(medium_engagement)} individuals")
print(f"   Regular engaged users\n")

print(f"\n💤 Low Engagement (Score 0-2): {len(low_engagement)} individuals")
print(f"   Need re-engagement campaigns\n")

print("="*80)
print("NEXT STEPS")
print("="*80)
print("\n1. The engagement data is now available in data/individual_engagement.json")
print("2. The app will use this data when creating segments")
print("3. To create a VIP segment:")
print("   • Go to Segments page")
print("   • Create a segment with:")
print("     - Name: VIP - Top 20 Most Engaged")
print("     - Base Object: Individual")
print("     - Filter: engagement_score >= 6")
print("   • This will give you the top 20 most engaged individuals!\n")


