#!/usr/bin/env python3
"""
Calculate channel-specific engagement scores for each individual
and determine preferred channel based on highest score
"""
import json
import random

def calculate_channel_scores():
    """Calculate engagement scores for each channel"""
    
    # Load engagement data
    with open('data/synthetic_engagement.json', 'r') as f:
        engagement_data = json.load(f)
    
    print(f"Processing {len(engagement_data)} individuals...")
    
    for individual in engagement_data:
        # Get metrics for each channel (normalize to 0-100 scale)
        
        # EMAIL SCORE (based on opens, clicks, deletes, bounces)
        email_opens = int(individual.get('email_opens', 0))
        email_clicks = int(individual.get('email_clicks', 0))
        email_deletes = int(individual.get('email_deletes', 0))
        email_campaigns = int(individual.get('email_campaigns_received', 0))
        email_bounces = int(individual.get('email_bounces', 0))
        
        if email_campaigns > 0:
            email_open_rate = (email_opens / email_campaigns) * 100
            email_click_rate = (email_clicks / email_campaigns) * 100
            email_bounce_penalty = (email_bounces / email_campaigns) * 20
            email_delete_penalty = (email_deletes / max(1, email_opens)) * 50  # INCREASED: Deletes as % of opens
            email_score = max(0, min(100, (email_open_rate * 0.3 + email_click_rate * 0.5) - email_bounce_penalty - email_delete_penalty))
        else:
            email_score = 0
        
        # SMS SCORE (based on opens, clicks, deletes, opt-outs)
        sms_sends = int(individual.get('sms_sends', 0))
        sms_opens = int(individual.get('sms_opens', 0))
        sms_clicks = int(individual.get('sms_clicks', 0))
        sms_deletes = int(individual.get('sms_deletes', 0))
        sms_optouts = int(individual.get('sms_optouts', 0))
        
        if sms_sends > 0:
            sms_open_rate = (sms_opens / sms_sends) * 100
            sms_click_rate = (sms_clicks / sms_sends) * 100
            sms_delete_penalty = (sms_deletes / max(1, sms_opens)) * 40  # INCREASED: Deletes as % of opens
            sms_optout_penalty = (sms_optouts / sms_sends) * 50
            sms_score = max(0, min(100, (sms_open_rate * 0.4 + sms_click_rate * 0.5) - sms_delete_penalty - sms_optout_penalty))
        else:
            sms_score = 0
        
        # WHATSAPP SCORE (based on opens, clicks, deletes, opt-outs)
        whatsapp_sends = int(individual.get('whatsapp_sends', 0))
        whatsapp_opens = int(individual.get('whatsapp_opens', 0))
        whatsapp_clicks = int(individual.get('whatsapp_clicks', 0))
        whatsapp_deletes = int(individual.get('whatsapp_deletes', 0))
        whatsapp_optouts = int(individual.get('whatsapp_optouts', 0))
        
        if whatsapp_sends > 0:
            whatsapp_open_rate = (whatsapp_opens / whatsapp_sends) * 100
            whatsapp_click_rate = (whatsapp_clicks / whatsapp_sends) * 100
            whatsapp_delete_penalty = (whatsapp_deletes / max(1, whatsapp_opens)) * 30  # INCREASED: Lower than others but still significant
            whatsapp_optout_penalty = (whatsapp_optouts / whatsapp_sends) * 50
            whatsapp_score = max(0, min(100, (whatsapp_open_rate * 0.3 + whatsapp_click_rate * 0.6) - whatsapp_delete_penalty - whatsapp_optout_penalty))
        else:
            whatsapp_score = 0
        
        # PUSH SCORE (based on opens, clicks, deletes)
        push_sends = int(individual.get('push_sends', 0))
        push_opens = int(individual.get('push_opens', 0))
        push_clicks = int(individual.get('push_clicks', 0))
        push_deletes = int(individual.get('push_deletes', 0))
        
        if push_sends > 0:
            push_open_rate = (push_opens / push_sends) * 100
            push_click_rate = (push_clicks / push_sends) * 100
            push_delete_penalty = (push_deletes / max(1, push_opens)) * 45  # INCREASED: Push notifications often dismissed
            push_score = max(0, min(100, (push_open_rate * 0.4 + push_click_rate * 0.5) - push_delete_penalty))
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
        
        # SOCIAL MEDIA SCORE (based on views, clicks)
        social_views = int(individual.get('social_views', 0))
        social_clicks = int(individual.get('social_clicks', 0))
        
        if social_views > 0:
            # Normalize views (assume 100 views = 100%)
            social_view_score = min(100, (social_views / 100) * 100)
            social_click_rate = (social_clicks / social_views) * 100
            social_score = (social_view_score * 0.4 + social_click_rate * 0.6)
        else:
            social_score = 0
        
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
        
        # Get omnichannel score for this individual
        omnichannel_score = float(individual.get('omnichannel_score', 0))
        
        # For highly engaged individuals (omni score > 5), distribute across channels
        # This ensures better channel distribution and prevents all top users going to one channel
        if omnichannel_score > 5:
            # Get top 3 channels by score (minimum 15 score threshold)
            sorted_channels = sorted(channel_scores.items(), key=lambda x: x[1], reverse=True)
            top_channels = [(ch, score) for ch, score in sorted_channels if score >= 15]
            
            if len(top_channels) >= 2:
                # Use weighted random selection from top channels
                # Give more weight to higher scores but allow distribution
                channels = [ch for ch, _ in top_channels[:3]]
                weights = [score ** 1.5 for _, score in top_channels[:3]]  # Square root weighting for balanced distribution
                
                # Normalize weights
                total_weight = sum(weights)
                if total_weight > 0:
                    weights = [w / total_weight for w in weights]
                    preferred_channel = random.choices(channels, weights=weights, k=1)[0]
                    preferred_channel_score = channel_scores[preferred_channel]
                else:
                    preferred_channel = max(channel_scores, key=channel_scores.get)
                    preferred_channel_score = channel_scores[preferred_channel]
            else:
                # Only one channel above threshold, use it
                preferred_channel = max(channel_scores, key=channel_scores.get)
                preferred_channel_score = channel_scores[preferred_channel]
        else:
            # For lower engagement individuals, use simple highest score
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

