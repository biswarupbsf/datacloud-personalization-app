#!/usr/bin/env python3
"""
Calculate channel-specific engagement scores for each individual
and determine preferred channel based on highest score
"""
import json

def calculate_channel_scores():
    """Calculate engagement scores for each channel"""
    
    # Load engagement data
    with open('data/synthetic_engagement.json', 'r') as f:
        engagement_data = json.load(f)
    
    print(f"Processing {len(engagement_data)} individuals...")
    
    for individual in engagement_data:
        # Get metrics for each channel (normalize to 0-100 scale)
        
        # EMAIL SCORE (based on opens, clicks, campaigns engaged)
        email_opens = int(individual.get('email_opens', 0))
        email_clicks = int(individual.get('email_clicks', 0))
        email_campaigns = int(individual.get('email_campaigns_received', 0))
        email_bounces = int(individual.get('email_bounces', 0))
        
        if email_campaigns > 0:
            email_open_rate = (email_opens / email_campaigns) * 100
            email_click_rate = (email_clicks / email_campaigns) * 100
            email_bounce_penalty = (email_bounces / email_campaigns) * 20
            email_score = min(100, (email_open_rate * 0.4 + email_click_rate * 0.6) - email_bounce_penalty)
        else:
            email_score = 0
        
        # SMS SCORE (based on opens, clicks, opt-outs)
        sms_sends = int(individual.get('sms_sends', 0))
        sms_opens = int(individual.get('sms_opens', 0))
        sms_clicks = int(individual.get('sms_clicks', 0))
        sms_optouts = int(individual.get('sms_optouts', 0))
        
        if sms_sends > 0:
            sms_open_rate = (sms_opens / sms_sends) * 100
            sms_click_rate = (sms_clicks / sms_sends) * 100
            sms_optout_penalty = (sms_optouts / sms_sends) * 50
            sms_score = min(100, (sms_open_rate * 0.5 + sms_click_rate * 0.5) - sms_optout_penalty)
        else:
            sms_score = 0
        
        # WHATSAPP SCORE (based on reads, replies)
        whatsapp_sends = int(individual.get('whatsapp_sends', 0))
        whatsapp_reads = int(individual.get('whatsapp_reads', 0))
        whatsapp_replies = int(individual.get('whatsapp_replies', 0))
        whatsapp_optouts = int(individual.get('whatsapp_optouts', 0))
        
        if whatsapp_sends > 0:
            whatsapp_read_rate = (whatsapp_reads / whatsapp_sends) * 100
            whatsapp_reply_rate = (whatsapp_replies / whatsapp_sends) * 100
            whatsapp_optout_penalty = (whatsapp_optouts / whatsapp_sends) * 50
            whatsapp_score = min(100, (whatsapp_read_rate * 0.4 + whatsapp_reply_rate * 0.6) - whatsapp_optout_penalty)
        else:
            whatsapp_score = 0
        
        # PUSH SCORE (based on opens, clicks)
        push_sends = int(individual.get('push_sends', 0))
        push_opens = int(individual.get('push_opens', 0))
        push_clicks = int(individual.get('push_clicks', 0))
        
        if push_sends > 0:
            push_open_rate = (push_opens / push_sends) * 100
            push_click_rate = (push_clicks / push_sends) * 100
            push_score = min(100, push_open_rate * 0.5 + push_click_rate * 0.5)
        else:
            push_score = 0
        
        # WEBSITE SCORE (based on views, add to cart, purchases)
        website_views = int(individual.get('website_product_views', 0))
        website_cart = int(individual.get('website_add_to_cart', 0))
        website_purchases = int(individual.get('website_purchases', 0))
        
        # Normalize website score (assuming max 50 views is 100%)
        view_score = min(100, (website_views / 50) * 100)
        cart_score = min(100, (website_cart / 20) * 100)
        purchase_score = min(100, (website_purchases / 10) * 100)
        website_score = (view_score * 0.3 + cart_score * 0.3 + purchase_score * 0.4)
        
        # SOCIAL MEDIA SCORE (generate from engagement patterns)
        # If they engage with email/web, they likely engage with social too
        social_base = (email_score + website_score) / 2
        # Add some variance
        import random
        social_variance = random.uniform(-20, 20)
        social_score = max(0, min(100, social_base + social_variance))
        
        # Store channel scores
        individual['email_engagement_score'] = round(email_score, 1)
        individual['sms_engagement_score'] = round(sms_score, 1)
        individual['whatsapp_engagement_score'] = round(whatsapp_score, 1)
        individual['push_engagement_score'] = round(push_score, 1)
        individual['website_engagement_score'] = round(website_score, 1)
        individual['social_engagement_score'] = round(social_score, 1)
        
        # Determine preferred channel based on highest score
        channel_scores = {
            'Email': email_score,
            'SMS': sms_score,
            'WhatsApp': whatsapp_score,
            'Push': push_score,
            'Website': website_score,
            'Social': social_score
        }
        
        # Get channel with highest score
        preferred_channel = max(channel_scores, key=channel_scores.get)
        preferred_channel_score = channel_scores[preferred_channel]
        
        # Only set preferred channel if score is above threshold
        if preferred_channel_score >= 10:
            individual['preferred_channel'] = preferred_channel
            individual['preferred_channel_score'] = round(preferred_channel_score, 1)
        else:
            # Default to email if no channel has good engagement
            individual['preferred_channel'] = 'Email'
            individual['preferred_channel_score'] = round(email_score, 1)
    
    # Save updated data
    with open('data/synthetic_engagement.json', 'w') as f:
        json.dump(engagement_data, f, indent=2)
    
    print(f"✅ Calculated channel scores for {len(engagement_data)} individuals")
    
    # Show statistics
    print("\n📊 Preferred Channel Distribution:")
    channel_distribution = {}
    for individual in engagement_data:
        channel = individual['preferred_channel']
        channel_distribution[channel] = channel_distribution.get(channel, 0) + 1
    
    for channel, count in sorted(channel_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"   {channel}: {count} individuals")
    
    print("\n📈 Average Channel Scores:")
    avg_scores = {
        'Email': sum(i['email_engagement_score'] for i in engagement_data) / len(engagement_data),
        'SMS': sum(i['sms_engagement_score'] for i in engagement_data) / len(engagement_data),
        'WhatsApp': sum(i['whatsapp_engagement_score'] for i in engagement_data) / len(engagement_data),
        'Push': sum(i['push_engagement_score'] for i in engagement_data) / len(engagement_data),
        'Website': sum(i['website_engagement_score'] for i in engagement_data) / len(engagement_data),
        'Social': sum(i['social_engagement_score'] for i in engagement_data) / len(engagement_data),
    }
    
    for channel, score in sorted(avg_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"   {channel}: {score:.1f}/100")

if __name__ == '__main__':
    calculate_channel_scores()

