#!/usr/bin/env python3
"""
Send Personalized Content to 5 Segment Members
Includes: Warm salutation (VIP/non-VIP), Product offers, Generated images
Test emails sent to: bbanerjee@salesforce.com and ursonly_rup@yahoo.co.uk
"""

import json
import os
from datetime import datetime
from simple_salesforce import Salesforce

# Test email recipients
TEST_EMAILS = [
    "bbanerjee@salesforce.com",
    "ursonly_rup@yahoo.co.uk"
]

# The 5 segment members
SEGMENT_MEMBERS = [
    "Biswarup Banerjee",
    "Ashish Desai",
    "Deepika Chauhan",
    "Rajesh Rao",
    "Archana Tripathi"
]

def load_individual_data():
    """Load engagement and insights data"""
    engagement_file = 'data/synthetic_engagement.json'
    insights_file = 'data/individual_insights.json'
    
    with open(engagement_file, 'r') as f:
        engagement_data = json.load(f)
    
    with open(insights_file, 'r') as f:
        insights_data = json.load(f)
    
    return engagement_data, insights_data

def get_vip_status(engagement_score):
    """Determine VIP status based on engagement score"""
    if engagement_score >= 7.0:
        return "VIP", "🌟 Exceptional VIP Member"
    elif engagement_score >= 6.0:
        return "VIP", "⭐ Premium VIP Member"
    elif engagement_score >= 5.0:
        return "Standard", "Valued Member"
    else:
        return "Standard", "Member"

def get_salutation(vip_status, name, engagement_score):
    """Generate warm salutation based on VIP status"""
    first_name = name.split()[0] if name else "Friend"
    
    if vip_status == "VIP":
        if engagement_score >= 7.0:
            return f"🌟 Dear {first_name},<br><br>As one of our <strong>Exceptional VIP Members</strong>, we're thrilled to bring you exclusive personalized content crafted just for you!"
        else:
            return f"⭐ Dear {first_name},<br><br>As a <strong>Premium VIP Member</strong>, we're excited to share personalized content designed specifically for you!"
    else:
        return f"Dear {first_name},<br><br>Thank you for being a valued member! We've created personalized content just for you."

def get_product_offers(insights):
    """Generate product offers based on insights"""
    offers = []
    
    # Fitness milestone offer
    fitness_milestone = insights.get('Fitness_Milestone', '')
    if fitness_milestone in ['Advanced', 'Elite']:
        offers.append({
            'title': f'🎉 {fitness_milestone} Premium Subscription - 50% OFF',
            'description': f'Celebrate your {fitness_milestone} fitness level with our premium subscription at half price!',
            'cta': 'Claim Your Discount',
            'discount': '50%'
        })
    
    # Health profile offer
    health_profile = insights.get('Health_Profile', '')
    if health_profile in ['Healthy', 'Fit', 'Active']:
        offers.append({
            'title': '💪 Premium Fitness Equipment Bundle',
            'description': 'Get the latest fitness gear from your favorite brand at special member pricing.',
            'cta': 'Shop Now',
            'discount': '30%'
        })
    
    # Favorite brand offer
    favourite_brand = insights.get('Favourite_Brand', '')
    if favourite_brand:
        offers.append({
            'title': f'🏷️ Exclusive {favourite_brand} Collection',
            'description': f'Special access to {favourite_brand} products with member-only pricing.',
            'cta': 'Explore Collection',
            'discount': '25%'
        })
    
    # Vacation/flight offer
    imminent_event = insights.get('Imminent_Event', '')
    if imminent_event and 'vacation' in imminent_event.lower():
        offers.append({
            'title': '✈️ Flight Booking Special',
            'description': 'Book your flights to your favorite destination with exclusive member rates.',
            'cta': 'Book Flights',
            'discount': '15%'
        })
    
    # Guitar hobby offer
    hobby = insights.get('Hobby', '')
    if hobby and 'guitar' in hobby.lower():
        offers.append({
            'title': '🎸 Guitar Purchase - 30% Discount',
            'description': 'Special discount on premium guitars for music enthusiasts.',
            'cta': 'Buy Guitar',
            'discount': '30%'
        })
    
    return offers

def generate_image_for_individual(individual, insights_data):
    """Generate personalized image for individual"""
    try:
        from modules.personalized_image_generator import PersonalizedImageGenerator
        
        # Get latest insights
        individual_insights = sorted(
            [i for i in insights_data if i.get('Individual_Name') == individual['Name']],
            key=lambda x: x.get('Event_Timestamp', ''),
            reverse=True
        )
        
        if not individual_insights:
            return None
        
        latest_insight = individual_insights[0]
        
        # Merge insights into individual data
        individual['fitness_milestone'] = latest_insight.get('Fitness_Milestone')
        individual['favourite_brand'] = latest_insight.get('Favourite_Brand')
        individual['favourite_destination'] = latest_insight.get('Favourite_Destination')
        individual['hobby'] = latest_insight.get('Hobby')
        individual['favourite_exercise'] = latest_insight.get('Favourite_Exercise', 'Treadmill Running')
        individual['health_profile'] = latest_insight.get('Health_Profile')
        individual['imminent_event'] = latest_insight.get('Imminent_Event', '')
        
        # Generate image
        image_generator = PersonalizedImageGenerator()
        result = image_generator.generate_personalized_image(individual)
        
        if result.get('success'):
            return result.get('image_url')
        else:
            print(f"  ⚠️  Image generation failed: {result.get('error')}")
            return None
    except Exception as e:
        print(f"  ⚠️  Could not generate image: {e}")
        return None

def generate_email_html(individual, engagement_data, insights_data, image_url=None):
    """Generate personalized email HTML"""
    
    # Get latest insights
    individual_insights = sorted(
        [i for i in insights_data if i.get('Individual_Name') == individual['Name']],
        key=lambda x: x.get('Event_Timestamp', ''),
        reverse=True
    )
    
    latest_insight = individual_insights[0] if individual_insights else {}
    
    # Get engagement score
    engagement_score = float(individual.get('engagement_score', individual.get('omnichannel_score', 5.0)))
    vip_status, vip_label = get_vip_status(engagement_score)
    
    # Get salutation
    salutation = get_salutation(vip_status, individual['Name'], engagement_score)
    
    # Get product offers
    offers = get_product_offers(latest_insight)
    
    # Get preferred channel
    preferred_channel = individual.get('preferred_channel', 'Email')
    
    # Build HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .vip-badge {{
            display: inline-block;
            background: gold;
            color: #333;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px 0;
            font-size: 14px;
        }}
        .content {{
            padding: 30px;
        }}
        .salutation {{
            font-size: 16px;
            margin-bottom: 20px;
            color: #555;
        }}
        .offers-section {{
            margin: 30px 0;
        }}
        .offer-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
        }}
        .offer-title {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .offer-description {{
            color: #666;
            margin-bottom: 15px;
        }}
        .cta-button {{
            background: #667eea;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            font-weight: bold;
            transition: background 0.3s;
        }}
        .cta-button:hover {{
            background: #5568d3;
        }}
        .image-section {{
            margin: 30px 0;
            text-align: center;
        }}
        .personalized-image {{
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin: 20px 0;
        }}
        .insights-summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .insight-item {{
            margin: 10px 0;
            padding: 8px;
            background: white;
            border-radius: 5px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Personalized Content for You</h1>
            <div class="vip-badge">{vip_label}</div>
            <p style="margin-top: 10px;">Engagement Score: {engagement_score:.2f}</p>
        </div>
        
        <div class="content">
            <div class="salutation">
                {salutation}
            </div>
            
            <div class="offers-section">
                <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                    🎁 Exclusive Offers Just for You
                </h2>
"""
    
    # Add offers
    for offer in offers:
        html += f"""
                <div class="offer-card">
                    <div class="offer-title">{offer['title']}</div>
                    <div class="offer-description">{offer['description']}</div>
                    <a href="#" class="cta-button">{offer['cta']} - {offer['discount']} OFF</a>
                </div>
"""
    
    # Add personalized image if available
    if image_url:
        html += f"""
            <div class="image-section">
                <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                    🎨 Your Personalized Image
                </h2>
                <img src="{image_url}" alt="Personalized Content" class="personalized-image" />
                <p style="color: #666; margin-top: 10px;">
                    Generated based on your favorite exercise, brand, and destination!
                </p>
            </div>
"""
    
    # Add insights summary
    if latest_insight:
        html += f"""
            <div class="insights-summary">
                <h3 style="color: #667eea;">📊 Your Profile Summary</h3>
                <div class="insight-item"><strong>Favorite Exercise:</strong> {latest_insight.get('Favourite_Exercise', 'N/A')}</div>
                <div class="insight-item"><strong>Favorite Brand:</strong> {latest_insight.get('Favourite_Brand', 'N/A')}</div>
                <div class="insight-item"><strong>Favorite Destination:</strong> {latest_insight.get('Favourite_Destination', 'N/A')}</div>
                <div class="insight-item"><strong>Fitness Milestone:</strong> {latest_insight.get('Fitness_Milestone', 'N/A')}</div>
                <div class="insight-item"><strong>Health Profile:</strong> {latest_insight.get('Health_Profile', 'N/A')}</div>
                <div class="insight-item"><strong>Preferred Channel:</strong> {preferred_channel}</div>
            </div>
"""
    
    html += """
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e0e0e0;">
                <p style="text-align: center; color: #666;">
                    This content was personalized using AI based on your engagement history and preferences.
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p>Thank you for being a valued member!</p>
            <p>This is a test email sent for demonstration purposes.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def send_test_emails():
    """Send personalized content emails to test addresses"""
    
    # Load data
    engagement_data, insights_data = load_individual_data()
    
    # Connect to Salesforce
    print("="*80)
    print("SENDING PERSONALIZED CONTENT EMAILS")
    print("="*80)
    
    username = os.environ.get('SF_USERNAME', 'biswarupb@salesforce.com')
    password = os.environ.get('SF_PASSWORD', 'SFTut0r25')
    
    print(f"\n→ Connecting to Salesforce as {username}...")
    try:
        sf = Salesforce(username=username, password=password, security_token="")
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Process each segment member
    results = []
    
    for member_name in SEGMENT_MEMBERS:
        print(f"\n{'='*80}")
        print(f"Processing: {member_name}")
        print(f"{'='*80}")
        
        # Find individual in engagement data
        individual = None
        for ind in engagement_data:
            if ind.get('Name') == member_name:
                individual = ind
                break
        
        if not individual:
            print(f"⚠️  {member_name} not found in engagement data")
            continue
        
        # Generate personalized image
        print(f"  → Generating personalized image...")
        image_url = generate_image_for_individual(individual, insights_data)
        
        if not image_url:
            # Fallback to profile picture
            image_url = individual.get('profile_picture_url', '')
            print(f"  ⚠️  Using profile picture as fallback")
        else:
            print(f"  ✅ Image generated: {image_url[:80]}...")
        
        # Generate email HTML
        html_content = generate_email_html(individual, engagement_data, insights_data, image_url)
        
        # Get engagement score for subject
        engagement_score = float(individual.get('engagement_score', individual.get('omnichannel_score', 5.0)))
        vip_status, vip_label = get_vip_status(engagement_score)
        preferred_channel = individual.get('preferred_channel', 'Email')
        
        subject = f"🎯 Personalized Content for {member_name} - {vip_label} ({preferred_channel})"
        
        print(f"  Engagement Score: {engagement_score:.2f}")
        print(f"  VIP Status: {vip_status}")
        print(f"  Preferred Channel: {preferred_channel}")
        print(f"  Subject: {subject}")
        
        # Send to test emails
        for test_email in TEST_EMAILS:
            print(f"\n  → Sending to {test_email}...")
            
            try:
                email_payload = {
                    "inputs": [{
                        "emailAddresses": test_email,
                        "emailSubject": f"[TEST] {subject}",
                        "emailBody": html_content,
                        "senderType": "CurrentUser"
                    }]
                }
                
                result = sf.restful(
                    'actions/standard/emailSimple',
                    method='POST',
                    data=json.dumps(email_payload)
                )
                
                print(f"  ✅ Sent successfully to {test_email}")
                results.append({
                    'recipient': test_email,
                    'individual': member_name,
                    'status': 'sent',
                    'subject': subject
                })
                
            except Exception as e:
                print(f"  ❌ Failed to send to {test_email}: {str(e)}")
                results.append({
                    'recipient': test_email,
                    'individual': member_name,
                    'status': 'failed',
                    'error': str(e)
                })
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total emails attempted: {len(results)}")
    print(f"Successful: {len([r for r in results if r['status'] == 'sent'])}")
    print(f"Failed: {len([r for r in results if r['status'] == 'failed'])}")
    
    # Save results
    with open('personalized_email_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to personalized_email_results.json")
    print(f"\n📧 Check your inbox at:")
    for email in TEST_EMAILS:
        print(f"   - {email}")

if __name__ == '__main__':
    send_test_emails()

