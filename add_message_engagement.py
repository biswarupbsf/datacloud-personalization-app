#!/usr/bin/env python3
"""
Add SMS/WhatsApp/Push Message Engagement to Synthetic Data
Creates comprehensive multi-channel engagement including:
- Email (opens, clicks, bounces)
- Website (views, cart, purchases)
- SMS (sends, opens, clicks, opt-outs)
- WhatsApp (sends, reads, replies)
- Push Notifications (sends, opens, clicks)
"""

from simple_salesforce import Salesforce
import json
import random
import requests
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta

# Connection details
USERNAME = "biswarupb@salesforce.com"
PASSWORD = "SFTut0r25"

print("="*80)
print("ADDING SMS/WHATSAPP/PUSH ENGAGEMENT TO SYNTHETIC DATA")
print("="*80)

# Connect
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
    print(f"❌ Login failed")
    exit(1)

root = ET.fromstring(response.text)
ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/', 'urn': 'urn:partner.soap.sforce.com'}
session_id = root.find('.//urn:sessionId', ns).text
server_url = root.find('.//urn:serverUrl', ns).text
instance_url = '/'.join(server_url.split('/')[:3])

sf = Salesforce(instance_url=instance_url, session_id=session_id)
print(f"✅ Connected to {instance_url}\n")

# Load existing synthetic data
print("Step 1: Loading existing synthetic engagement data...")
try:
    with open('data/synthetic_engagement.json', 'r') as f:
        existing_data = json.load(f)
    print(f"Found {len(existing_data)} individuals with email + website engagement\n")
except FileNotFoundError:
    print("❌ Synthetic engagement file not found. Run create_synthetic_engagement.py first.")
    exit(1)

# Add message engagement to each individual
print("Step 2: Adding SMS/WhatsApp/Push engagement...")

enhanced_data = []

for individual in existing_data:
    # Determine engagement tier based on existing score
    score = individual.get('engagement_score', 0)
    
    # SMS ENGAGEMENT
    if score >= 4:  # High engagement
        sms_sends = random.randint(12, 25)
        sms_opens = random.randint(10, 22)
        sms_clicks = random.randint(5, 15)
        sms_optouts = 0
    elif score >= 2:  # Medium engagement
        sms_sends = random.randint(6, 14)
        sms_opens = random.randint(3, 12)
        sms_clicks = random.randint(1, 8)
        sms_optouts = 0 if random.random() > 0.1 else 1
    else:  # Low engagement
        sms_sends = random.randint(1, 6)
        sms_opens = random.randint(0, 4)
        sms_clicks = random.randint(0, 2)
        sms_optouts = 1 if random.random() > 0.7 else 0
    
    # WHATSAPP ENGAGEMENT
    if score >= 4:
        whatsapp_sends = random.randint(8, 20)
        whatsapp_reads = random.randint(7, 18)
        whatsapp_replies = random.randint(3, 12)
        whatsapp_optouts = 0
    elif score >= 2:
        whatsapp_sends = random.randint(4, 10)
        whatsapp_reads = random.randint(2, 9)
        whatsapp_replies = random.randint(1, 5)
        whatsapp_optouts = 0
    else:
        whatsapp_sends = random.randint(0, 5)
        whatsapp_reads = random.randint(0, 3)
        whatsapp_replies = random.randint(0, 2)
        whatsapp_optouts = 1 if random.random() > 0.8 else 0
    
    # PUSH NOTIFICATIONS
    if score >= 4:
        push_sends = random.randint(15, 30)
        push_opens = random.randint(10, 25)
        push_clicks = random.randint(5, 15)
    elif score >= 2:
        push_sends = random.randint(8, 18)
        push_opens = random.randint(4, 14)
        push_clicks = random.randint(2, 8)
    else:
        push_sends = random.randint(2, 10)
        push_opens = random.randint(0, 6)
        push_clicks = random.randint(0, 3)
    
    # Calculate new engagement score including message channels
    email_score = (individual['email_opens'] * 0.5) + (individual['email_clicks'] * 1.0)
    website_score = (individual['website_product_views'] * 0.2) + (individual['website_purchases'] * 2.0)
    sms_score = (sms_opens * 0.4) + (sms_clicks * 0.8) - (sms_optouts * 2.0)
    whatsapp_score = (whatsapp_reads * 0.5) + (whatsapp_replies * 1.5)
    push_score = (push_opens * 0.3) + (push_clicks * 0.6)
    
    combined_score = (email_score + website_score + sms_score + whatsapp_score + push_score) / 15
    normalized_score = max(0, min(10, int(combined_score)))
    
    # Enhance individual data
    enhanced = individual.copy()
    enhanced.update({
        # SMS
        'sms_sends': sms_sends,
        'sms_opens': sms_opens,
        'sms_clicks': sms_clicks,
        'sms_optouts': sms_optouts,
        'sms_open_rate': round((sms_opens / sms_sends * 100) if sms_sends > 0 else 0, 1),
        
        # WhatsApp
        'whatsapp_sends': whatsapp_sends,
        'whatsapp_reads': whatsapp_reads,
        'whatsapp_replies': whatsapp_replies,
        'whatsapp_optouts': whatsapp_optouts,
        'whatsapp_read_rate': round((whatsapp_reads / whatsapp_sends * 100) if whatsapp_sends > 0 else 0, 1),
        
        # Push Notifications
        'push_sends': push_sends,
        'push_opens': push_opens,
        'push_clicks': push_clicks,
        'push_open_rate': round((push_opens / push_sends * 100) if push_sends > 0 else 0, 1),
        
        # Combined metrics
        'total_message_sends': sms_sends + whatsapp_sends + push_sends,
        'total_message_interactions': sms_opens + sms_clicks + whatsapp_reads + whatsapp_replies + push_opens + push_clicks,
        'preferred_channel': max(
            ('Email', email_score),
            ('Website', website_score),
            ('SMS', sms_score),
            ('WhatsApp', whatsapp_score),
            ('Push', push_score),
            key=lambda x: x[1]
        )[0],
        
        # Updated overall engagement score
        'engagement_score': normalized_score,
        'omnichannel_score': round(combined_score, 2),
        'data_source': 'synthetic_omnichannel'
    })
    
    enhanced_data.append(enhanced)

# Sort by engagement score
enhanced_data.sort(key=lambda x: x['engagement_score'], reverse=True)

print(f"✅ Added message engagement for {len(enhanced_data)} individuals\n")

# Save enhanced data
output_file = 'data/synthetic_engagement.json'
with open(output_file, 'w') as f:
    json.dump(enhanced_data, f, indent=2)

print(f"✅ Saved omnichannel engagement to {output_file}\n")

# Show summary
print("="*80)
print("OMNICHANNEL ENGAGEMENT SUMMARY")
print("="*80)

# Top 20
print(f"\n🌟 Top 20 Most Engaged (Omnichannel):")
print(f"{'Rank':<6} {'Name':<25} {'Email':<10} {'SMS':<10} {'WhatsApp':<10} {'Push':<10} {'Score':<6}")
print("-" * 90)

for i, eng in enumerate(enhanced_data[:20], 1):
    email_str = f"{eng['email_opens']}/{eng['email_clicks']}"
    sms_str = f"{eng['sms_opens']}/{eng['sms_clicks']}"
    wa_str = f"{eng['whatsapp_reads']}/{eng['whatsapp_replies']}"
    push_str = f"{eng['push_opens']}/{eng['push_clicks']}"
    print(f"{i:<6} {eng['name']:<25} {email_str:<10} {sms_str:<10} {wa_str:<10} {push_str:<10} {eng['engagement_score']:<6}")

# Channel breakdown
print(f"\n📊 Channel Performance:")
print(f"{'Channel':<15} {'Sends':<12} {'Interactions':<15} {'Avg Rate':<12}")
print("-" * 60)

total_email_sends = sum(e['email_campaigns_received'] for e in enhanced_data)
total_email_interactions = sum(e['email_opens'] + e['email_clicks'] for e in enhanced_data)
avg_email_rate = (total_email_interactions / total_email_sends * 100) if total_email_sends > 0 else 0

total_sms = sum(e['sms_sends'] for e in enhanced_data)
total_sms_inter = sum(e['sms_opens'] + e['sms_clicks'] for e in enhanced_data)
avg_sms_rate = (total_sms_inter / total_sms * 100) if total_sms > 0 else 0

total_wa = sum(e['whatsapp_sends'] for e in enhanced_data)
total_wa_inter = sum(e['whatsapp_reads'] + e['whatsapp_replies'] for e in enhanced_data)
avg_wa_rate = (total_wa_inter / total_wa * 100) if total_wa > 0 else 0

total_push = sum(e['push_sends'] for e in enhanced_data)
total_push_inter = sum(e['push_opens'] + e['push_clicks'] for e in enhanced_data)
avg_push_rate = (total_push_inter / total_push * 100) if total_push > 0 else 0

print(f"{'Email':<15} {total_email_sends:<12,} {total_email_interactions:<15,} {avg_email_rate:<12.1f}%")
print(f"{'SMS':<15} {total_sms:<12,} {total_sms_inter:<15,} {avg_sms_rate:<12.1f}%")
print(f"{'WhatsApp':<15} {total_wa:<12,} {total_wa_inter:<15,} {avg_wa_rate:<12.1f}%")
print(f"{'Push':<15} {total_push:<12,} {total_push_inter:<15,} {avg_push_rate:<12.1f}%")

# Preferred channels
print(f"\n💬 Preferred Communication Channels:")
channel_counts = {}
for e in enhanced_data:
    channel = e['preferred_channel']
    channel_counts[channel] = channel_counts.get(channel, 0) + 1

for channel, count in sorted(channel_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {channel}: {count} individuals")

print("\n" + "="*80)
print("✅ OMNICHANNEL ENGAGEMENT DATA READY!")
print("="*80)
print("\nYour synthetic data now includes:")
print("✅ Email engagement (opens, clicks, bounces)")
print("✅ Website engagement (views, cart, purchases)")
print("✅ SMS engagement (opens, clicks, opt-outs)")
print("✅ WhatsApp engagement (reads, replies)")
print("✅ Push notifications (opens, clicks)")
print("✅ Omnichannel engagement scores")
print("✅ Preferred channel identification")


