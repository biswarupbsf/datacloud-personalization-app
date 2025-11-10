#!/usr/bin/env python3
"""
Create Synthetic Email + Website Engagement Data for Test Individuals
Includes: Email opens, clicks, bounces + Website product views, cart events, purchases
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
print("CREATING SYNTHETIC ENGAGEMENT DATA (EMAIL + WEBSITE)")
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

# Fetch test individuals
print("Step 1: Fetching Test Individuals...")
individuals_query = "SELECT Id, Name FROM Individual ORDER BY Name LIMIT 100"
individuals = sf.query(individuals_query)['records']
print(f"Found {len(individuals)} individuals\n")

# Product catalog for synthetic data
products = [
    {'name': 'Wireless Headphones', 'price': 79.99, 'category': 'Electronics'},
    {'name': 'Running Shoes', 'price': 129.99, 'category': 'Sports'},
    {'name': 'Smart Watch', 'price': 249.99, 'category': 'Electronics'},
    {'name': 'Yoga Mat', 'price': 34.99, 'category': 'Sports'},
    {'name': 'Coffee Maker', 'price': 89.99, 'category': 'Home'},
    {'name': 'Backpack', 'price': 59.99, 'category': 'Accessories'},
    {'name': 'Bluetooth Speaker', 'price': 99.99, 'category': 'Electronics'},
    {'name': 'Water Bottle', 'price': 24.99, 'category': 'Sports'},
    {'name': 'Desk Lamp', 'price': 44.99, 'category': 'Home'},
    {'name': 'Phone Case', 'price': 19.99, 'category': 'Accessories'},
    {'name': 'Laptop Stand', 'price': 39.99, 'category': 'Office'},
    {'name': 'Fitness Tracker', 'price': 149.99, 'category': 'Sports'},
    {'name': 'Wireless Mouse', 'price': 29.99, 'category': 'Electronics'},
    {'name': 'Notebook Set', 'price': 15.99, 'category': 'Office'},
    {'name': 'Travel Mug', 'price': 22.99, 'category': 'Home'}
]

# Email campaigns
email_campaigns = [
    'Weekly Newsletter',
    'Product Launch Announcement',
    'Flash Sale Alert',
    'Personalized Recommendations',
    'Cart Abandonment Reminder',
    'Welcome Email',
    'Customer Survey',
    'Seasonal Promotion'
]

print("Step 2: Generating Synthetic Engagement Data...")
engagement_data = []

for i, individual in enumerate(individuals):
    # Create engagement tiers (Top 20%, Middle 50%, Bottom 30%)
    percentile = (i + 1) / len(individuals)
    
    # EMAIL ENGAGEMENT
    if percentile <= 0.20:  # Top 20% - High engagement
        email_opens = random.randint(15, 30)
        email_clicks = random.randint(10, 20)
        email_bounces = random.randint(0, 1)
        email_unsubscribes = 0
    elif percentile <= 0.70:  # Middle 50% - Medium engagement
        email_opens = random.randint(5, 14)
        email_clicks = random.randint(2, 9)
        email_bounces = random.randint(0, 2)
        email_unsubscribes = 0 if random.random() > 0.1 else 1
    else:  # Bottom 30% - Low engagement
        email_opens = random.randint(0, 4)
        email_clicks = random.randint(0, 2)
        email_bounces = random.randint(0, 3)
        email_unsubscribes = 1 if random.random() > 0.7 else 0
    
    # WEBSITE ENGAGEMENT
    if percentile <= 0.20:  # High website engagement
        product_views = random.randint(20, 50)
        add_to_cart = random.randint(5, 15)
        cart_abandons = random.randint(1, 5)
        purchases = random.randint(3, 10)
    elif percentile <= 0.70:  # Medium website engagement
        product_views = random.randint(8, 19)
        add_to_cart = random.randint(2, 7)
        cart_abandons = random.randint(1, 3)
        purchases = random.randint(1, 4)
    else:  # Low website engagement
        product_views = random.randint(0, 7)
        add_to_cart = random.randint(0, 3)
        cart_abandons = random.randint(0, 2)
        purchases = random.randint(0, 1)
    
    # Generate browsed products
    browsed_products = random.sample(products, min(random.randint(3, 10), len(products)))
    
    # Generate purchased products
    num_purchases = min(purchases, len(browsed_products))
    purchased_products = random.sample(browsed_products, num_purchases) if num_purchases > 0 else []
    
    # Calculate total order value
    total_order_value = sum(p['price'] for p in purchased_products)
    
    # Calculate engagement score (0-10)
    email_score = (email_opens * 0.5) + (email_clicks * 1.0) - (email_bounces * 0.5) - (email_unsubscribes * 2.0)
    website_score = (product_views * 0.2) + (add_to_cart * 0.5) + (purchases * 2.0) - (cart_abandons * 0.3)
    
    combined_score = (email_score + website_score) / 10
    normalized_score = max(0, min(10, int(combined_score)))
    
    # Generate email campaign interactions
    num_campaigns_received = random.randint(5, 15)
    campaigns_engaged = random.sample(email_campaigns, min(num_campaigns_received, len(email_campaigns)))
    
    engagement_data.append({
        'id': individual['Id'],
        'name': individual['Name'],
        
        # Email Engagement
        'email_opens': email_opens,
        'email_clicks': email_clicks,
        'email_bounces': email_bounces,
        'email_unsubscribes': email_unsubscribes,
        'email_campaigns_received': num_campaigns_received,
        'email_campaigns_engaged': campaigns_engaged,
        
        # Website Engagement
        'website_product_views': product_views,
        'website_add_to_cart': add_to_cart,
        'website_cart_abandons': cart_abandons,
        'website_purchases': purchases,
        'products_browsed': [p['name'] for p in browsed_products],
        'products_purchased': [p['name'] for p in purchased_products],
        'total_order_value': round(total_order_value, 2),
        'favorite_category': max(set([p['category'] for p in browsed_products]), 
                                key=[p['category'] for p in browsed_products].count) if browsed_products else 'None',
        
        # Combined Metrics
        'engagement_score': normalized_score,
        'last_engagement_date': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        'data_source': 'synthetic'
    })

# Sort by engagement score
engagement_data.sort(key=lambda x: x['engagement_score'], reverse=True)

print(f"✅ Generated synthetic engagement for {len(engagement_data)} individuals\n")

# Save to JSON
output_file = 'data/synthetic_engagement.json'
with open(output_file, 'w') as f:
    json.dump(engagement_data, f, indent=2)

print(f"✅ Saved to {output_file}\n")

# Show summary
print("="*80)
print("SYNTHETIC ENGAGEMENT DATA SUMMARY")
print("="*80)

# Top 20
print(f"\n🌟 Top 20 Most Engaged (Synthetic Data):")
print(f"{'Rank':<6} {'Name':<30} {'Email':<15} {'Website':<15} {'Score':<6}")
print(f"{'':6} {'':30} {'Opens/Clicks':<15} {'Views/Purchases':<15}")
print("-" * 80)

for i, eng in enumerate(engagement_data[:20], 1):
    email_str = f"{eng['email_opens']}/{eng['email_clicks']}"
    web_str = f"{eng['website_product_views']}/{eng['website_purchases']}"
    print(f"{i:<6} {eng['name']:<30} {email_str:<15} {web_str:<15} {eng['engagement_score']:<6}")

# Distribution
high = len([e for e in engagement_data if e['engagement_score'] >= 7])
med = len([e for e in engagement_data if 3 <= e['engagement_score'] < 7])
low = len([e for e in engagement_data if e['engagement_score'] < 3])

print(f"\n📊 Engagement Distribution:")
print(f"   High (7-10): {high} individuals - ${sum(e['total_order_value'] for e in engagement_data if e['engagement_score'] >= 7):.2f} total revenue")
print(f"   Medium (3-6): {med} individuals - ${sum(e['total_order_value'] for e in engagement_data if 3 <= e['engagement_score'] < 7):.2f} total revenue")
print(f"   Low (0-2): {low} individuals - ${sum(e['total_order_value'] for e in engagement_data if e['engagement_score'] < 3):.2f} total revenue")

print(f"\n💰 Total Revenue: ${sum(e['total_order_value'] for e in engagement_data):.2f}")
print(f"📧 Total Email Opens: {sum(e['email_opens'] for e in engagement_data):,}")
print(f"🖱️  Total Email Clicks: {sum(e['email_clicks'] for e in engagement_data):,}")
print(f"👁️  Total Product Views: {sum(e['website_product_views'] for e in engagement_data):,}")
print(f"🛒 Total Purchases: {sum(e['website_purchases'] for e in engagement_data)}")

print("\n" + "="*80)
print("✅ SYNTHETIC ENGAGEMENT DATA READY!")
print("="*80)





