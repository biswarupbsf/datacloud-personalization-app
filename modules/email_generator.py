"""
Email Generator
Generates and sends personalized emails
"""

import json
import os
from datetime import datetime
import random

class EmailGenerator:
    
    def __init__(self):
        self.templates_dir = 'templates/email_templates'
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """Ensure templates directory exists"""
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Create default VIP template if not exists
        vip_template = os.path.join(self.templates_dir, 'vip_welcome.json')
        if not os.path.exists(vip_template):
            self._create_default_vip_template()
    
    def _create_default_vip_template(self):
        """Create default VIP welcome template"""
        template = {
            'id': 'vip_welcome',
            'name': 'VIP Welcome Email',
            'description': 'Personalized VIP welcome email with engagement stats',
            'subject_template': '🌟 {greeting}, {first_name}!',
            'html_template': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
        .highlight { background: #f8f9fa; padding: 20px; border-left: 4px solid #667eea; 
                     margin: 20px 0; border-radius: 5px; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { text-align: center; padding: 15px; background: #f8f9fa; 
                    border-radius: 8px; flex: 1; margin: 0 10px; }
        .stat-number { font-size: 32px; font-weight: bold; color: #667eea; }
        .stat-label { font-size: 12px; color: #666; text-transform: uppercase; }
        .cta-button { background: #667eea; color: white; padding: 15px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block; 
                      margin: 20px 0; font-weight: bold; }
        .vip-badge { display: inline-block; background: gold; color: #333; 
                     padding: 5px 15px; border-radius: 20px; font-weight: bold; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 Welcome to VIP Status! 🌟</h1>
            <div class="vip-badge">{vip_level}</div>
        </div>
        <div class="content">
            <h2>Dear {full_name},</h2>
            <p><strong>Congratulations!</strong> {stars} Your exceptional engagement has earned you VIP status.</p>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">{metric_1}</div>
                    <div class="stat-label">{metric_1_label}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{metric_2}</div>
                    <div class="stat-label">{metric_2_label}</div>
                </div>
            </div>
            <div class="highlight">
                <h3>🎁 Your Exclusive Benefits</h3>
                <p>{benefits}</p>
            </div>
            <center>
                <a href="{cta_link}" class="cta-button">{cta_text}</a>
            </center>
            <p>{personal_note}</p>
        </div>
    </div>
</body>
</html>
            ''',
            'variables': [
                'greeting', 'first_name', 'full_name', 'vip_level', 'stars',
                'metric_1', 'metric_1_label', 'metric_2', 'metric_2_label',
                'benefits', 'cta_link', 'cta_text', 'personal_note'
            ]
        }
        
        with open(os.path.join(self.templates_dir, 'vip_welcome.json'), 'w') as f:
            json.dump(template, f, indent=2)
    
    def list_templates(self):
        """List available email templates"""
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.templates_dir, filename), 'r') as f:
                    template = json.load(f)
                    templates.append({
                        'id': template['id'],
                        'name': template['name'],
                        'description': template['description']
                    })
        return templates
    
    def generate_personalized_emails(self, sf, segment_id, template_id, customizations=None):
        """Generate personalized emails for a segment"""
        from modules.segmentation_engine import SegmentationEngine
        
        seg_engine = SegmentationEngine()
        segment_data = seg_engine.get_segment_members(sf, segment_id)
        members = segment_data['members']
        
        # Load template
        template_path = os.path.join(self.templates_dir, f'{template_id}.json')
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        emails = []
        for i, member in enumerate(members):
            # Generate personalization data
            personalization = self._generate_personalization_data(member, i, len(members), customizations)
            
            # Generate subject
            subject = self._render_template(template['subject_template'], personalization)
            
            # Generate HTML body
            html_body = self._render_template(template['html_template'], personalization)
            
            emails.append({
                'recipient_id': member['Id'],
                'recipient_name': member.get('Name', 'Valued Customer'),
                'recipient_email': personalization.get('email', 'unknown@example.com'),
                'subject': subject,
                'html_body': html_body,
                'personalization': personalization
            })
        
        return emails
    
    def send_emails(self, sf, emails):
        """Send generated emails via Salesforce"""
        results = []
        
        for email in emails:
            try:
                # Use Salesforce emailSimple action
                email_payload = {
                    "inputs": [{
                        "emailAddresses": email['recipient_email'],
                        "emailSubject": email['subject'],
                        "emailBody": email['html_body'],
                        "senderType": "CurrentUser"
                    }]
                }
                
                result = sf.restful(
                    'actions/standard/emailSimple',
                    method='POST',
                    data=json.dumps(email_payload)
                )
                
                results.append({
                    'recipient': email['recipient_email'],
                    'status': 'sent',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'recipient': email['recipient_email'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def preview_email(self, template_id, recipient_data, customizations=None):
        """Preview an email with sample data"""
        template_path = os.path.join(self.templates_dir, f'{template_id}.json')
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        personalization = self._generate_personalization_data(recipient_data, 0, 1, customizations)
        html = self._render_template(template['html_template'], personalization)
        
        return html
    
    def _generate_personalization_data(self, member, index, total, customizations=None):
        """Generate personalization data for a member"""
        name = member.get('Name', 'Valued Customer')
        first_name = name.split()[-1] if name else 'Friend'
        
        data = {
            'full_name': name,
            'first_name': first_name,
            'greeting': self._get_greeting(index, total),
            'vip_level': self._get_vip_level(index, total),
            'stars': self._get_stars(index, total),
            'metric_1': random.randint(5, 20),
            'metric_1_label': 'Engagements',
            'metric_2': random.randint(2, 10),
            'metric_2_label': 'Actions',
            'benefits': 'Priority support, exclusive content, early access to new features',
            'cta_link': '#',
            'cta_text': 'Claim Your Benefits',
            'personal_note': f'Thank you for being an engaged member, {first_name}!',
            'email': member.get('Email', f'{first_name.lower()}@example.com')
        }
        
        if customizations:
            data.update(customizations)
        
        return data
    
    def _get_greeting(self, index, total):
        """Get personalized greeting based on rank"""
        if index == 0:
            return "You're Our #1 Champion"
        elif index < total * 0.1:
            return "Welcome to VIP"
        else:
            return "Exclusive VIP Access for You"
    
    def _get_vip_level(self, index, total):
        """Get VIP level based on rank"""
        if index < total * 0.1:
            return "VIP MEMBER - EXCEPTIONAL"
        elif index < total * 0.3:
            return "VIP MEMBER - OUTSTANDING"
        else:
            return "VIP MEMBER - EXCELLENT"
    
    def _get_stars(self, index, total):
        """Get star rating based on rank"""
        if index < total * 0.1:
            return "🌟🌟🌟"
        elif index < total * 0.3:
            return "🌟🌟"
        else:
            return "🌟"
    
    def _render_template(self, template_str, data):
        """Render template with data"""
        result = template_str
        for key, value in data.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result
    
    def get_engagement_analytics(self, sf, segment_id):
        """Get engagement analytics for a segment"""
        # This is simulated - in production, you'd query actual email engagement data
        return {
            'total_sent': random.randint(50, 200),
            'total_opens': random.randint(30, 150),
            'total_clicks': random.randint(10, 80),
            'open_rate': random.uniform(40, 80),
            'click_rate': random.uniform(10, 40),
            'bounce_rate': random.uniform(1, 5)
        }


