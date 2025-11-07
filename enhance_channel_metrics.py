#!/usr/bin/env python3
"""
Enhance synthetic data with detailed channel metrics
Add: deletes for messaging channels, separate views/clicks for social and website
"""
import json
import random

def enhance_channel_metrics():
    """Add detailed metrics for each channel"""
    
    # Load engagement data
    with open('data/synthetic_engagement.json', 'r') as f:
        engagement_data = json.load(f)
    
    print(f"Enhancing {len(engagement_data)} individuals with detailed channel metrics...")
    
    for individual in engagement_data:
        # EMAIL: Already has opens, clicks - add deletes
        email_opens = int(individual.get('email_opens', 0))
        email_clicks = int(individual.get('email_clicks', 0))
        # Deletes are typically 10-30% of opens
        email_deletes = random.randint(int(email_opens * 0.1), int(email_opens * 0.3))
        individual['email_deletes'] = email_deletes
        
        # SMS: Already has opens, clicks - add deletes
        sms_opens = int(individual.get('sms_opens', 0))
        sms_clicks = int(individual.get('sms_clicks', 0))
        # SMS deletes are typically 5-15% of opens (lower than email)
        sms_deletes = random.randint(int(sms_opens * 0.05), int(sms_opens * 0.15))
        individual['sms_deletes'] = sms_deletes
        
        # WHATSAPP: Has reads - rename to opens, has replies - add clicks and deletes
        whatsapp_reads = int(individual.get('whatsapp_reads', 0))
        whatsapp_replies = int(individual.get('whatsapp_replies', 0))
        individual['whatsapp_opens'] = whatsapp_reads  # Opens = Reads
        # Clicks are typically 40-60% of opens for WhatsApp (high engagement)
        whatsapp_clicks = random.randint(int(whatsapp_reads * 0.4), int(whatsapp_reads * 0.6))
        individual['whatsapp_clicks'] = whatsapp_clicks
        # WhatsApp deletes are very low (2-8%)
        whatsapp_deletes = random.randint(int(whatsapp_reads * 0.02), int(whatsapp_reads * 0.08))
        individual['whatsapp_deletes'] = whatsapp_deletes
        
        # PUSH: Already has opens, clicks - add deletes
        push_opens = int(individual.get('push_opens', 0))
        push_clicks = int(individual.get('push_clicks', 0))
        # Push deletes are typically 20-40% (people dismiss notifications)
        push_deletes = random.randint(int(push_opens * 0.2), int(push_opens * 0.4))
        individual['push_deletes'] = push_deletes
        
        # SOCIAL MEDIA: Create views and clicks
        # Based on engagement patterns, social views should be moderate
        social_views = random.randint(20, 100)
        # Social clicks are typically 5-15% of views
        social_clicks = random.randint(int(social_views * 0.05), int(social_views * 0.15))
        individual['social_views'] = social_views
        individual['social_clicks'] = social_clicks
        
        # WEBSITE: Already has views - add website_clicks (separate from add_to_cart)
        website_views = int(individual.get('website_product_views', 0))
        # Website clicks (on products) are typically 30-50% of views
        website_clicks = random.randint(int(website_views * 0.3), int(website_views * 0.5))
        individual['website_clicks'] = website_clicks
    
    # Save updated data
    with open('data/synthetic_engagement.json', 'w') as f:
        json.dump(engagement_data, f, indent=2)
    
    print(f"✅ Enhanced {len(engagement_data)} individuals with detailed channel metrics")
    
    # Show sample metrics
    print("\n📊 Sample Individual Metrics:")
    sample = engagement_data[0]
    print(f"\n{sample.get('Name', 'Unknown')}:")
    print(f"  📧 Email: Opens={sample.get('email_opens')}, Clicks={sample.get('email_clicks')}, Deletes={sample.get('email_deletes')}")
    print(f"  📱 SMS: Opens={sample.get('sms_opens')}, Clicks={sample.get('sms_clicks')}, Deletes={sample.get('sms_deletes')}")
    print(f"  💬 WhatsApp: Opens={sample.get('whatsapp_opens')}, Clicks={sample.get('whatsapp_clicks')}, Deletes={sample.get('whatsapp_deletes')}")
    print(f"  🔔 Push: Opens={sample.get('push_opens')}, Clicks={sample.get('push_clicks')}, Deletes={sample.get('push_deletes')}")
    print(f"  👥 Social: Views={sample.get('social_views')}, Clicks={sample.get('social_clicks')}")
    print(f"  🌐 Website: Views={sample.get('website_product_views')}, Clicks={sample.get('website_clicks')}")

if __name__ == '__main__':
    enhance_channel_metrics()

