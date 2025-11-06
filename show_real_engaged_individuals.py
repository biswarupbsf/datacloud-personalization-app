#!/usr/bin/env python3
"""
Show REAL Engaged Individuals from Data Cloud
(Not the test individuals, but the real ones with engagement history)
"""

from simple_salesforce import Salesforce
import json
import requests
from xml.etree import ElementTree as ET
from collections import defaultdict

# Connection details
USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"

print("="*80)
print("DISCOVERING REAL ENGAGED INDIVIDUALS FROM DATA CLOUD")
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

# Get top engaged individuals directly from email engagement data
print("Finding individuals with most email engagement...")

# Query to get individuals with engagement counts
email_query = """
    SELECT IndividualId__c, EngagementChannelActionId__c, COUNT(Id) engagement_count 
    FROM BU2_EmailEngagement__dlm 
    WHERE IndividualId__c != null 
    GROUP BY IndividualId__c, EngagementChannelActionId__c
    LIMIT 5000
"""

engagement_results = sf.query(email_query)['records']
print(f"Retrieved {len(engagement_results)} engagement records\n")

# Aggregate by individual
individual_engagement = defaultdict(lambda: {'opens': 0, 'clicks': 0, 'sends': 0, 'bounces': 0, 'total': 0})

for record in engagement_results:
    ind_id = record.get('IndividualId__c')
    action_id = str(record.get('EngagementChannelActionId__c', ''))
    count = record.get('engagement_count', 0)
    
    if ind_id:
        individual_engagement[ind_id]['total'] += count
        
        # Map action ID to type (adjust based on your org's action IDs)
        if action_id == '2':
            individual_engagement[ind_id]['opens'] += count
        elif action_id == '3':
            individual_engagement[ind_id]['clicks'] += count
        elif action_id == '1':
            individual_engagement[ind_id]['sends'] += count
        elif action_id == '4':
            individual_engagement[ind_id]['bounces'] += count

# Sort by total engagement
top_individuals = sorted(individual_engagement.items(), key=lambda x: x[1]['total'], reverse=True)[:50]

print(f"Found {len(top_individuals)} highly engaged individuals!")
print("\nFetching their details from Individual object...\n")

# Get Individual records for top engaged
individual_ids = [ind_id for ind_id, _ in top_individuals]
individual_ids_str = "','".join(individual_ids[:50])  # Limit to 50 for query

individual_query = f"SELECT Id, Name, FirstName, LastName FROM Individual WHERE Id IN ('{individual_ids_str}')"
individuals = sf.query(individual_query)['records']

# Create lookup
individual_lookup = {ind['Id']: ind for ind in individuals}

# Create final engagement data
final_data = []
for ind_id, engagement in top_individuals[:50]:
    ind_record = individual_lookup.get(ind_id, {})
    
    # Calculate score
    score = (
        engagement['opens'] * 1.0 +
        engagement['clicks'] * 2.0 +
        engagement['sends'] * 0.5 -
        engagement['bounces'] * 0.5
    )
    normalized_score = min(10, int(score / 10))
    
    final_data.append({
        'id': ind_id,
        'name': ind_record.get('Name', 'Unknown'),
        'first_name': ind_record.get('FirstName', ''),
        'last_name': ind_record.get('LastName', ''),
        'opens': engagement['opens'],
        'clicks': engagement['clicks'],
        'sends': engagement['sends'],
        'bounces': engagement['bounces'],
        'total_engagements': engagement['total'],
        'engagement_score': normalized_score,
        'data_source': 'real_datacloud'
    })

# Save to JSON
output_file = 'data/real_engaged_individuals.json'
with open(output_file, 'w') as f:
    json.dump(final_data, f, indent=2)

print(f"✅ Saved {len(final_data)} real engaged individuals to {output_file}\n")

# Display top 20
print("="*80)
print("🌟 TOP 20 REAL ENGAGED INDIVIDUALS FROM DATA CLOUD")
print("="*80)
print(f"\n{'Rank':<6} {'Name':<35} {'Opens':<8} {'Clicks':<8} {'Total':<8} {'Score':<6}")
print("-" * 80)

for i, eng in enumerate(final_data[:20], 1):
    print(f"{i:<6} {eng['name']:<35} {eng['opens']:<8} {eng['clicks']:<8} {eng['total_engagements']:<8} {eng['engagement_score']:<6}")

print("\n" + "="*80)
print("✅ REAL DATA CLOUD INTEGRATION COMPLETE!")
print("="*80)
print("\nThese are REAL individuals from your Data Cloud with actual engagement history!")
print("\nNext steps:")
print("1. I can update the app to show THESE real individuals instead of test data")
print("2. Or we can keep both: test individuals + real engaged individuals")
print("3. Create VIP segments from the real engaged individuals")

