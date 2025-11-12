#!/usr/bin/env python3
"""
Data Cloud Management Application
A comprehensive tool to manage Salesforce Data Cloud
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import secrets

# Import custom modules
from modules.salesforce_connector import SalesforceManager
from modules.oauth_connector import OAuthConnector
from modules.simple_auth import SimpleAuthConnector
from modules.data_manager import DataManager
from modules.relationship_builder import RelationshipBuilder
from modules.segmentation_engine import SegmentationEngine
from modules.email_generator import EmailGenerator
from modules.datacloud_analytics import DataCloudAnalytics
from modules.ai_agent import AIAgent
from modules.personalized_image_generator import PersonalizedImageGenerator

app = Flask(__name__)
# Use environment variable for secret key (consistent across restarts)
# If not set, generate one (for development)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('PORT') is not None  # True on Heroku
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global managers
sf_manager = SalesforceManager()
oauth_manager = OAuthConnector()
simple_auth_manager = SimpleAuthConnector()
data_manager = DataManager()
relationship_builder = RelationshipBuilder()
segmentation_engine = SegmentationEngine()
email_generator = EmailGenerator()
datacloud_analytics = DataCloudAnalytics()
ai_agent = AIAgent()
image_generator = PersonalizedImageGenerator()

# Auto-connect to Salesforce if credentials are in environment variables
def auto_connect_salesforce():
    """Automatically connect to Salesforce using environment variables"""
    sf_username = os.environ.get('SF_USERNAME')
    sf_password = os.environ.get('SF_PASSWORD')
    sf_security_token = os.environ.get('SF_SECURITY_TOKEN', '')
    
    if sf_username and sf_password:
        try:
            print(f"🔄 Auto-connecting to Salesforce as {sf_username}...")
            sf_manager.connect(sf_username, sf_password, sf_security_token)
            print(f"✅ Auto-connected to Salesforce successfully!")
            print(f"   Instance: {sf_manager.instance_url}")
            return True
        except Exception as e:
            print(f"⚠️ Auto-connect failed: {str(e)}")
            return False
    return False

# Try auto-connect on startup
AUTO_CONNECTED = auto_connect_salesforce()

# ============================================================================
# AUTHENTICATION & CONNECTION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page / Dashboard"""
    # Check if auto-connected or manually connected via session
    if not sf_manager.is_connected() and 'connected' not in session:
        return redirect(url_for('login'))
    
    # If auto-connected but no session, create one
    if AUTO_CONNECTED and 'connected' not in session:
        session['connected'] = True
        session['username'] = os.environ.get('SF_USERNAME', 'Auto-connected User')
        session.permanent = True
    
    # Get dashboard stats
    stats = data_manager.get_dashboard_stats(sf_manager.sf)
    username = session.get('username', os.environ.get('SF_USERNAME', 'User'))
    return render_template('dashboard.html', stats=stats, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page to connect to Salesforce"""
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    security_token = data.get('security_token', '')
    
    try:
        sf_manager.connect(username, password, security_token)
        session['connected'] = True
        session['username'] = username
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Connected successfully!',
            'org_info': sf_manager.get_org_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/login/oauth', methods=['POST'])
def login_oauth():
    """Simple SOAP login with optional security token"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    security_token = data.get('security_token', '')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    try:
        # Connect using SOAP (token appended to password if provided)
        simple_auth_manager.connect_soap(username, password, security_token)
        
        # Copy connection to sf_manager for compatibility
        sf_manager.sf = simple_auth_manager.sf
        sf_manager.username = simple_auth_manager.username
        sf_manager.instance_url = simple_auth_manager.instance_url
        sf_manager.org_id = simple_auth_manager.org_id
        sf_manager.connected_at = simple_auth_manager.connected_at
        
        session['connected'] = True
        session['username'] = simple_auth_manager.username
        session['password'] = password  # Store for auto-reconnect after app reload
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Connected successfully!',
            'org_info': simple_auth_manager.get_org_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/login/auto', methods=['POST'])
def login_auto():
    """Auto-login using environment variables (no user input needed)"""
    try:
        # Get credentials from environment variables
        username = os.environ.get('SF_USERNAME')
        password = os.environ.get('SF_PASSWORD')
        
        if not username or not password:
            return jsonify({
                'success': False, 
                'error': 'SF_USERNAME and SF_PASSWORD environment variables not set on Heroku'
            }), 400
        
        # Connect using SOAP (no token needed)
        simple_auth_manager.connect_soap(username, password, '')
        
        # Copy connection to sf_manager for compatibility
        sf_manager.sf = simple_auth_manager.sf
        sf_manager.username = simple_auth_manager.username
        sf_manager.instance_url = simple_auth_manager.instance_url
        sf_manager.org_id = simple_auth_manager.org_id
        sf_manager.connected_at = simple_auth_manager.connected_at
        
        session['connected'] = True
        session['username'] = simple_auth_manager.username
        session['password'] = password  # Store for auto-reconnect after app reload
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': f'Connected successfully as {username}!',
            'org_info': simple_auth_manager.get_org_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/connection/status')
def connection_status():
    """Check connection status"""
    if sf_manager.is_connected():
        return jsonify({
            'connected': True,
            'org_info': sf_manager.get_org_info()
        })
    return jsonify({'connected': False})

# ============================================================================
# DATA MANAGEMENT ROUTES
# ============================================================================

@app.route('/data')
def data_management():
    """Data management interface"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('data_management.html')

@app.route('/api/data/objects')
def get_objects():
    """Get list of available Salesforce objects"""
    objects = data_manager.get_available_objects(sf_manager.sf)
    return jsonify(objects)

@app.route('/api/data/<object_name>/fields')
def get_object_fields(object_name):
    """Get fields for a specific object"""
    fields = data_manager.get_object_fields(sf_manager.sf, object_name)
    return jsonify(fields)

@app.route('/api/data/<object_name>/records')
def get_records(object_name):
    """Get records for an object"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    records = data_manager.get_records(sf_manager.sf, object_name, limit, offset)
    return jsonify(records)

@app.route('/api/data/<object_name>/create', methods=['POST'])
def create_record(object_name):
    """Create a new record"""
    data = request.get_json()
    try:
        result = data_manager.create_record(sf_manager.sf, object_name, data)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/data/<object_name>/bulk-create', methods=['POST'])
def bulk_create_records(object_name):
    """Bulk create records"""
    data = request.get_json()
    count = data.get('count', 1)
    template = data.get('template', {})
    
    try:
        results = data_manager.bulk_create_records(
            sf_manager.sf, object_name, count, template
        )
        return jsonify({'success': True, 'created': len(results), 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/data/<object_name>/<record_id>', methods=['PUT'])
def update_record(object_name, record_id):
    """Update a record"""
    data = request.get_json()
    try:
        result = data_manager.update_record(sf_manager.sf, object_name, record_id, data)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/data/<object_name>/<record_id>', methods=['DELETE'])
def delete_record(object_name, record_id):
    """Delete a record"""
    try:
        result = data_manager.delete_record(sf_manager.sf, object_name, record_id)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# RELATIONSHIP BUILDER ROUTES
# ============================================================================

@app.route('/relationships')
def relationships():
    """Relationship builder interface"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('relationships.html')

@app.route('/api/relationships/discover')
def discover_relationships():
    """Discover relationships between objects"""
    object_name = request.args.get('object', 'Individual')
    relationships = relationship_builder.discover_relationships(sf_manager.sf, object_name)
    return jsonify(relationships)

@app.route('/api/relationships/create', methods=['POST'])
def create_relationship():
    """Create a relationship between records"""
    data = request.get_json()
    try:
        result = relationship_builder.create_relationship(
            sf_manager.sf,
            data['parent_object'],
            data['parent_id'],
            data['child_object'],
            data['relationship_field'],
            data.get('additional_data', {})
        )
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/relationships/visualize')
def visualize_relationships():
    """Get relationship data for visualization"""
    object_name = request.args.get('object', 'Individual')
    depth = request.args.get('depth', 2, type=int)
    
    graph_data = relationship_builder.get_relationship_graph(
        sf_manager.sf, object_name, depth
    )
    return jsonify(graph_data)

# ============================================================================
# SEGMENTATION ROUTES
# ============================================================================

@app.route('/segments')
def segments():
    """Segmentation interface"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('segments.html')

@app.route('/api/segments/list')
def list_segments():
    """List all saved segments"""
    segments = segmentation_engine.list_segments()
    return jsonify(segments)

@app.route('/api/segments/create', methods=['POST'])
def create_segment():
    """Create a new segment"""
    data = request.get_json()
    try:
        result = segmentation_engine.create_segment(
            sf_manager.sf,
            data['name'],
            data['description'],
            data['base_object'],
            data['filters']
        )
        return jsonify({'success': True, 'segment': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/segments/<segment_id>/members')
def get_segment_members(segment_id):
    """Get members of a segment with enriched insights data"""
    members_data = segmentation_engine.get_segment_members(sf_manager.sf, segment_id)
    
    # Load individual insights data to enrich members with psychographic info
    try:
        insights_file = 'data/individual_insights.json'
        if os.path.exists(insights_file):
            with open(insights_file, 'r') as f:
                insights_data = json.load(f)
            
            # Create lookup by Individual_Id - get the most recent insight for each individual
            insights_by_id = {}
            for insight in insights_data:
                ind_id = insight.get('Individual_Id')
                if ind_id:
                    # Keep the most recent or just the last one in the file
                    insights_by_id[ind_id] = insight
            
            # Enrich members with insights data
            for member in members_data['members']:
                member_id = member.get('Id')
                if member_id and member_id in insights_by_id:
                    insight = insights_by_id[member_id]
                    member['Purchase_Intent'] = insight.get('Purchase_Intent', 'N/A')
                    member['Current_Sentiment'] = insight.get('Current_Sentiment', 'N/A')
                    member['Favourite_Brand'] = insight.get('Favourite_Brand', 'N/A')
                    member['Lifestyle_Quotient'] = insight.get('Lifestyle_Quotient', 'N/A')
                    member['Health_Profile'] = insight.get('Health_Profile', 'N/A')
                else:
                    # Add placeholder values if no insights found
                    member['Purchase_Intent'] = 'N/A'
                    member['Current_Sentiment'] = 'N/A'
                    member['Favourite_Brand'] = 'N/A'
                    member['Lifestyle_Quotient'] = 'N/A'
                    member['Health_Profile'] = 'N/A'
    except Exception as e:
        print(f"Error loading insights data: {e}")
        # Continue without insights data
    
    return jsonify(members_data)

@app.route('/api/segments/<segment_id>/sync', methods=['POST'])
def sync_segment_to_salesforce(segment_id):
    """Sync segment to Salesforce Campaign"""
    try:
        result = segmentation_engine.sync_to_campaign(sf_manager.sf, segment_id)
        return jsonify({'success': True, 'campaign': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/segments/preview', methods=['POST'])
def preview_segment():
    """Preview segment results before creating"""
    data = request.get_json()
    try:
        results = segmentation_engine.preview_segment(
            sf_manager.sf,
            data['base_object'],
            data['filters']
        )
        return jsonify({'success': True, 'count': len(results), 'sample': results[:10]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# EMAIL CAMPAIGN ROUTES
# ============================================================================

@app.route('/emails')
def emails():
    """Email campaign interface"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('emails.html')

@app.route('/api/emails/templates')
def get_email_templates():
    """Get available email templates"""
    templates = email_generator.list_templates()
    return jsonify(templates)

@app.route('/api/emails/generate', methods=['POST'])
def generate_emails():
    """Generate personalized emails for a segment"""
    data = request.get_json()
    try:
        results = email_generator.generate_personalized_emails(
            sf_manager.sf,
            data['segment_id'],
            data['template_id'],
            data.get('customizations', {})
        )
        return jsonify({'success': True, 'emails': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/emails/send', methods=['POST'])
def send_emails():
    """Send generated emails"""
    data = request.get_json()
    try:
        results = email_generator.send_emails(
            sf_manager.sf,
            data['emails']
        )
        return jsonify({'success': True, 'sent': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/emails/preview', methods=['POST'])
def preview_email():
    """Preview a personalized email"""
    data = request.get_json()
    try:
        html = email_generator.preview_email(
            data['template_id'],
            data['recipient_data'],
            data.get('customizations', {})
        )
        return jsonify({'success': True, 'html': html})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# ANALYTICS & REPORTING ROUTES
# ============================================================================

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/api/analytics/engagement')
def get_engagement_analytics():
    """Get email engagement analytics"""
    segment_id = request.args.get('segment_id')
    
    analytics = email_generator.get_engagement_analytics(
        sf_manager.sf,
        segment_id
    )
    return jsonify(analytics)

@app.route('/api/analytics/segments')
def get_segment_analytics():
    """Get segment analytics"""
    # Check if connected - if session exists but sf is None, try to reconnect
    if 'connected' not in session:
        return jsonify({
            'total_segments': 0,
            'total_members': 0,
            'synced_campaigns': 0,
            'segments_by_object': {},
            'error': 'Not logged in'
        })
    
    # Auto-reconnect if session exists but connection was lost (due to app reload)
    if not sf_manager.sf and 'username' in session and 'password' in session:
        try:
            simple_auth_manager.connect_soap(session['username'], session['password'])
            sf_manager.sf = simple_auth_manager.sf
        except:
            pass
    
    if not sf_manager.sf:
        return jsonify({
            'total_segments': 0,
            'total_members': 0,
            'synced_campaigns': 0,
            'segments_by_object': {},
            'error': 'Connection lost - please log in again'
        })
    
    analytics = segmentation_engine.get_segment_analytics(sf_manager.sf)
    return jsonify(analytics)

@app.route('/api/analytics/datacloud')
def get_datacloud_analytics():
    """Get real Data Cloud analytics"""
    if 'connected' not in session:
        return jsonify({
            'error': 'Not logged in',
            'total_records': {
                'email_engagements': 0,
                'message_engagements': 0,
                'website_events': 0,
                'orders': 0
            }
        })
    
    # Auto-reconnect if session exists but connection was lost (due to app reload)
    if not sf_manager.sf and 'username' in session and 'password' in session:
        try:
            simple_auth_manager.connect_soap(session['username'], session['password'])
            sf_manager.sf = simple_auth_manager.sf
        except:
            pass
    
    if not sf_manager.sf:
        return jsonify({
            'error': 'Connection lost - please log in again',
            'total_records': {
                'email_engagements': 0,
                'message_engagements': 0,
                'website_events': 0,
                'orders': 0
            }
        })
    
    try:
        analytics = datacloud_analytics.get_datacloud_summary(sf_manager.sf)
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analytics/datacloud/email')
def get_datacloud_email_stats():
    """Get real Data Cloud email engagement statistics"""
    try:
        stats = datacloud_analytics.get_email_engagement_stats(sf_manager.sf)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analytics/datacloud/website')
def get_datacloud_website_stats():
    """Get real Data Cloud website engagement statistics"""
    try:
        stats = datacloud_analytics.get_website_engagement_stats(sf_manager.sf)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analytics/insights')
def get_insights_analytics():
    """Get Individual Insights analytics"""
    try:
        from collections import Counter
        
        # Load insights data
        insights_file = 'data/individual_insights.json'
        if not os.path.exists(insights_file):
            return jsonify({
                'success': False,
                'error': 'Insights data not found',
                'message': 'Individual Insights data file is missing. Please generate it first.'
            }), 404
        
        with open(insights_file, 'r') as f:
            insights_data = json.load(f)
        
        if not insights_data:
            return jsonify({
                'success': False,
                'error': 'No insights data available'
            }), 404
        
        # Calculate analytics
        total_records = len(insights_data)
        unique_individuals = len(set(i['Individual_Id'] for i in insights_data))
        
        # Get distributions
        sentiments = Counter(i['Current_Sentiment'] for i in insights_data)
        lifestyles = Counter(i['Lifestyle_Quotient'] for i in insights_data)
        health_profiles = Counter(i['Health_Profile'] for i in insights_data)
        fitness_milestones = Counter(i['Fitness_Milestone'] for i in insights_data)
        purchase_intents = Counter(i['Purchase_Intent'] for i in insights_data)
        favorite_brands = Counter(i['Favourite_Brand'] for i in insights_data)
        favorite_destinations = Counter(i['Favourite_Destination'] for i in insights_data)
        hobbies = Counter(i['Hobby'] for i in insights_data)
        
        # Calculate time-based insights
        from datetime import datetime as dt
        timestamps = [dt.fromisoformat(i['Event_Timestamp'].replace('Z', '+00:00')) for i in insights_data]
        oldest_timestamp = min(timestamps).isoformat() if timestamps else None
        newest_timestamp = max(timestamps).isoformat() if timestamps else None
        
        analytics = {
            'success': True,
            'overview': {
                'total_records': total_records,
                'unique_individuals': unique_individuals,
                'records_per_individual': total_records // unique_individuals if unique_individuals > 0 else 0,
                'oldest_timestamp': oldest_timestamp,
                'newest_timestamp': newest_timestamp
            },
            'distributions': {
                'sentiments': dict(sentiments.most_common(10)),
                'lifestyles': dict(lifestyles.most_common(10)),
                'health_profiles': dict(health_profiles.most_common(10)),
                'fitness_milestones': dict(fitness_milestones),
                'purchase_intents': dict(purchase_intents),
                'favorite_brands': dict(favorite_brands.most_common(15)),
                'favorite_destinations': dict(favorite_destinations.most_common(15)),
                'hobbies': dict(hobbies.most_common(15))
            },
            'sample_records': insights_data[:20]  # First 20 records
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/individuals/<individual_id>/insights')
def get_individual_insights(individual_id):
    """Get insights for a specific individual"""
    try:
        # Load insights data
        insights_file = 'data/individual_insights.json'
        if not os.path.exists(insights_file):
            return jsonify({
                'success': False,
                'error': 'Insights data not found'
            }), 404
        
        with open(insights_file, 'r') as f:
            insights_data = json.load(f)
        
        # Filter by individual ID
        individual_insights = [i for i in insights_data if i['Individual_Id'] == individual_id]
        
        # Sort by timestamp descending (newest first)
        individual_insights.sort(key=lambda x: x['Event_Timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'individual_id': individual_id,
            'total_insights': len(individual_insights),
            'insights': individual_insights
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# AI AGENT ROUTES
# ============================================================================

@app.route('/agent')
def agent_page():
    """AI Agent chat interface"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('agent.html')

@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    """Process conversational request through AI agent"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        # Process through AI agent
        # Pass None for sf if not connected (synthetic data doesn't need Salesforce)
        sf_connection = sf_manager.sf if sf_manager.is_connected() else None
        response = ai_agent.process_request(
            user_message,
            sf_connection,
            data_manager,
            segmentation_engine,
            email_generator,
            datacloud_analytics,
            image_generator  # Pass image generator for personalized content
        )
        
        return jsonify({'success': True, 'response': response})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/agent/history')
def agent_history():
    """Get conversation history"""
    history = ai_agent.get_conversation_history()
    return jsonify({'success': True, 'history': history})

@app.route('/api/agent/clear', methods=['POST'])
def agent_clear():
    """Clear conversation history"""
    result = ai_agent.clear_history()
    return jsonify({'success': True, 'message': result['message']})

@app.route('/data/synthetic_engagement.json')
def serve_synthetic_engagement():
    """Serve synthetic engagement data file"""
    import os
    import json
    
    engagement_file = 'data/synthetic_engagement.json'
    if os.path.exists(engagement_file):
        with open(engagement_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({'error': 'Engagement data not found'}), 404

@app.route('/test-analytics')
def test_analytics_page():
    """Test page for debugging API calls"""
    return render_template('test_analytics.html')

@app.route('/view-generated-email/<path:filename>')
def view_generated_email(filename):
    """View generated HTML email"""
    try:
        file_path = os.path.join('generated_emails', filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content
        else:
            return f"<h1>File not found</h1><p>Could not find: {file_path}</p>", 404
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

@app.route('/list-generated-emails')
def list_generated_emails():
    """List all generated email files"""
    try:
        if not os.path.exists('generated_emails'):
            return jsonify({'emails': []})
        
        files = []
        for filename in os.listdir('generated_emails'):
            if filename.endswith('.html'):
                file_path = os.path.join('generated_emails', filename)
                stat = os.stat(file_path)
                files.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size': stat.st_size,
                    'preview_url': f'/view-generated-email/{filename}'
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify({'emails': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/individual-engagement')
def individual_engagement_page():
    """Individual engagement dashboard"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('individual_engagement.html')

@app.route('/individual-insights')
def individual_insights_page():
    """Individual insights dashboard"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('individual_insights.html')

@app.route('/data/individual_insights.json')
def serve_individual_insights():
    """Serve individual insights data file"""
    import os
    import json
    
    insights_file = 'data/individual_insights.json'
    if os.path.exists(insights_file):
        with open(insights_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({'error': 'Insights data not found'}), 404

@app.route('/individual-vehicle-telemetry')
def individual_vehicle_telemetry_page():
    """Individual driving insights dashboard"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('individual_vehicle_telemetry.html')

@app.route('/api/individual-telemetry')
def get_individual_telemetry():
    """Get individual driving insights profiles"""
    try:
        telemetry_file = 'data/individual_telemetry_summary.json'
        if not os.path.exists(telemetry_file):
            return jsonify({'error': 'Telemetry data not found'}), 404
        
        with open(telemetry_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vehicle-telemetry')
def vehicle_telemetry_page():
    """Vehicle telemetry events dashboard"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    return render_template('vehicle_telemetry.html')

@app.route('/api/vehicle-telemetry-events')
def get_vehicle_telemetry_events():
    """Get all vehicle telemetry events"""
    try:
        telemetry_file = 'data/vehicle_telematics.json'
        if not os.path.exists(telemetry_file):
            return jsonify({'error': 'Telemetry events data not found'}), 404
        
        with open(telemetry_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/individuals/engagement')
def get_individuals_engagement():
    """Get all individuals with their engagement metrics - directly from synthetic data"""
    try:
        # Load synthetic engagement data (contains all info including real names)
        engagement_file = 'data/synthetic_engagement.json'
        if not os.path.exists(engagement_file):
            return jsonify({'success': False, 'error': 'Engagement data not found'}), 404
        
        with open(engagement_file, 'r') as f:
            engagement_data = json.load(f)
        
        # Load individual insights data
        insights_file = 'data/individual_insights.json'
        insights_by_name = {}
        try:
            with open(insights_file, 'r') as f:
                insights_data = json.load(f)
            # Create lookup by name, get latest insight for each individual
            for insight in insights_data:
                name = insight.get('Individual_Name')
                if name:
                    if name not in insights_by_name or insight.get('Event_Timestamp', '') > insights_by_name[name].get('Event_Timestamp', ''):
                        insights_by_name[name] = insight
        except Exception as e:
            print(f"⚠️ Could not load insights: {e}")
        
        # Use data directly from synthetic_engagement.json (has real names and all metrics)
        merged_data = []
        for item in engagement_data:
            merged_data.append({
                'Id': item.get('id', ''),
                'Name': item.get('Name', 'Unknown'),
                'FirstName': item.get('FirstName', ''),
                'LastName': item.get('LastName', ''),
                'Email': item.get('Email', ''),
                'Phone': item.get('Phone', ''),
                'profile_picture_url': item.get('profile_picture_url', ''),
                'engagement_score': item.get('engagement_score', 0),
                'omnichannel_score': item.get('omnichannel_score', 0),
                # Email metrics
                'email_opens': item.get('email_opens', 0),
                'email_clicks': item.get('email_clicks', 0),
                'email_deletes': item.get('email_deletes', 0),
                'email_bounces': item.get('email_bounces', 0),
                'email_unsubscribes': item.get('email_unsubscribes', 0),
                # SMS metrics
                'sms_sends': item.get('sms_sends', 0),
                'sms_opens': item.get('sms_opens', 0),
                'sms_clicks': item.get('sms_clicks', 0),
                'sms_deletes': item.get('sms_deletes', 0),
                'sms_optouts': item.get('sms_optouts', 0),
                'sms_open_rate': item.get('sms_open_rate', 0),
                # WhatsApp metrics
                'whatsapp_sends': item.get('whatsapp_sends', 0),
                'whatsapp_opens': item.get('whatsapp_opens', 0),
                'whatsapp_clicks': item.get('whatsapp_clicks', 0),
                'whatsapp_deletes': item.get('whatsapp_deletes', 0),
                'whatsapp_replies': item.get('whatsapp_replies', 0),
                'whatsapp_optouts': item.get('whatsapp_optouts', 0),
                # Push metrics
                'push_sends': item.get('push_sends', 0),
                'push_opens': item.get('push_opens', 0),
                'push_clicks': item.get('push_clicks', 0),
                'push_deletes': item.get('push_deletes', 0),
                'push_open_rate': item.get('push_open_rate', 0),
                # Social metrics
                'social_views': item.get('social_views', 0),
                'social_clicks': item.get('social_clicks', 0),
                # Website metrics
                'website_product_views': item.get('website_product_views', 0),
                'website_clicks': item.get('website_clicks', 0),
                'website_add_to_cart': item.get('website_add_to_cart', 0),
                'website_cart_abandons': item.get('website_cart_abandons', 0),
                'website_purchases': item.get('website_purchases', 0),
                'total_order_value': item.get('total_order_value', 0),
                'total_message_sends': item.get('total_message_sends', 0),
                'total_message_interactions': item.get('total_message_interactions', 0),
                'preferred_channel': item.get('preferred_channel', 'Email'),
                'preferred_channel_score': item.get('preferred_channel_score', 0),
                'preferred_contact_time': item.get('preferred_contact_time', 'Not Set'),
                'email_engagement_score': item.get('email_engagement_score', 0),
                'sms_engagement_score': item.get('sms_engagement_score', 0),
                'whatsapp_engagement_score': item.get('whatsapp_engagement_score', 0),
                'push_engagement_score': item.get('push_engagement_score', 0),
                'website_engagement_score': item.get('website_engagement_score', 0),
                'social_engagement_score': item.get('social_engagement_score', 0),
                'products_browsed': item.get('products_browsed', []),
                'products_purchased': item.get('products_purchased', []),
                'favorite_category': item.get('favorite_category', ''),
                'last_engagement': item.get('last_engagement_date', '')
            })
            
            # Add insights if available
            name = item.get('Name')
            if name in insights_by_name:
                insight = insights_by_name[name]
                merged_data[-1]['insights'] = {
                    'Favourite_Exercise': insight.get('Favourite_Exercise'),
                    'Favourite_Brand': insight.get('Favourite_Brand'),
                    'Favourite_Destination': insight.get('Favourite_Destination'),
                    'Hobby': insight.get('Hobby'),
                    'Lifestyle_Quotient': insight.get('Lifestyle_Quotient'),
                    'Current_Sentiment': insight.get('Current_Sentiment'),
                    'Health_Profile': insight.get('Health_Profile'),
                    'Fitness_Milestone': insight.get('Fitness_Milestone'),
                    'Purchase_Intent': insight.get('Purchase_Intent'),
                    'Imminent_Event': insight.get('Imminent_Event')
                }
        
        # Sort by omnichannel score descending
        merged_data.sort(key=lambda x: x['omnichannel_score'], reverse=True)
        
        return jsonify({'success': True, 'individuals': merged_data, 'total': len(merged_data)})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug/status')
def debug_status():
    """Debug endpoint to check login status"""
    return jsonify({
        'session_connected': 'connected' in session,
        'sf_manager_connected': sf_manager.sf is not None,
        'session_keys': list(session.keys()),
        'sf_instance': sf_manager.sf.instance_url if sf_manager.sf else None
    })

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a custom SOQL query"""
    data = request.get_json()
    query = data.get('query')
    
    try:
        results = sf_manager.sf.query(query)
        return jsonify({'success': True, 'records': results['records']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/upload-profile-picture', methods=['GET', 'POST'])
def upload_profile_picture():
    """Upload profile picture for any individual (stores as base64 in JSON)"""
    if request.method == 'GET':
        # Load all individuals for dropdown
        try:
            data_file = os.path.join('data', 'synthetic_engagement.json')
            with open(data_file, 'r') as f:
                profiles = json.load(f)
            names_list = [p.get('Name', '') for p in profiles if p.get('Name')]
            names_options = ''.join([f'<option value="{name}">{name}</option>' for name in sorted(names_list)])
        except:
            names_options = '<option value="Biswarup Banerjee">Biswarup Banerjee</option>'
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Profile Picture</title>
            <style>
                body {{ font-family: Arial; max-width: 700px; margin: 50px auto; padding: 20px; background: #f5f7fa; }}
                h1 {{ color: #667eea; display: flex; align-items: center; justify-content: space-between; }}
                .home-btn {{ background: #4caf50; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-size: 14px; font-weight: bold; display: inline-block; }}
                .home-btn:hover {{ background: #45a049; }}
                .upload-box {{ background: white; border: 2px dashed #667eea; padding: 40px; text-align: center; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                select, input[type="file"] {{ width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
                button {{ background: #667eea; color: white; border: none; padding: 15px 40px; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; }}
                button:hover {{ background: #5568d3; }}
                .success {{ color: green; font-weight: bold; margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 5px; }}
                .error {{ color: red; font-weight: bold; margin-top: 20px; padding: 15px; background: #ffebee; border-radius: 5px; }}
                .preview {{ max-width: 200px; max-height: 200px; margin: 20px auto; border-radius: 10px; display: none; }}
                label {{ font-weight: 600; color: #333; display: block; margin-top: 15px; text-align: left; }}
            </style>
        </head>
        <body>
            <h1>
                <span>📸 Upload Profile Picture</span>
                <a href="/" class="home-btn">🏠 Home</a>
            </h1>
            <div class="upload-box">
                <p style="color: #666;">Upload profile pictures for any individual (Stored as base64 - works on Heroku!)</p>
                <form id="uploadForm">
                    <label>Select Individual:</label>
                    <select name="person_name" id="personName" required>
                        {names_options}
                    </select>
                    
                    <label>Choose Profile Picture (JPG, PNG, max 2MB):</label>
                    <input type="file" name="profile_picture" id="fileInput" accept="image/*" required>
                    
                    <img id="preview" class="preview" />
                    
                    <button type="submit">📤 Upload Picture</button>
                </form>
                <div id="message"></div>
            </div>
            <script>
                // Preview image
                document.getElementById('fileInput').onchange = (e) => {{
                    const file = e.target.files[0];
                    if (file) {{
                        const reader = new FileReader();
                        reader.onload = (e) => {{
                            const preview = document.getElementById('preview');
                            preview.src = e.target.result;
                            preview.style.display = 'block';
                        }};
                        reader.readAsDataURL(file);
                    }}
                }};
                
                // Upload
                document.getElementById('uploadForm').onsubmit = async (e) => {{
                    e.preventDefault();
                    
                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];
                    const personName = document.getElementById('personName').value;
                    
                    if (!file) {{
                        alert('Please select a file');
                        return;
                    }}
                    
                    // Read file as base64
                    const reader = new FileReader();
                    reader.onload = async (e) => {{
                        const base64Image = e.target.result;
                        
                        // Send to server
                        const response = await fetch('/upload-profile-picture', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                person_name: personName,
                                image_data: base64Image
                            }})
                        }});
                        
                        const result = await response.json();
                        const msgDiv = document.getElementById('message');
                        
                        if (result.success) {{
                            msgDiv.className = 'success';
                            msgDiv.textContent = '✅ ' + result.message + ' - Refresh Individual Engagement to see it!';
                        }} else {{
                            msgDiv.className = 'error';
                            msgDiv.textContent = '❌ ' + result.error;
                        }}
                    }};
                    
                    reader.readAsDataURL(file);
                }};
            </script>
        </body>
        </html>
        '''
    
    # Handle POST - upload to Cloudinary and save URL
    try:
        data = request.get_json()
        person_name = data.get('person_name')
        image_data = data.get('image_data')
        
        if not person_name or not image_data:
            return jsonify({'success': False, 'error': 'Missing person name or image data'}), 400
        
        # Upload to Cloudinary for PERMANENT storage
        import cloudinary
        import cloudinary.uploader
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
            api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
        )
        
        print(f"📤 Uploading profile picture for {person_name} to Cloudinary...")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            image_data,
            folder="profile_pictures",
            public_id=f"profile_{person_name.replace(' ', '_')}",
            overwrite=True,
            resource_type="image",
            transformation=[
                {'width': 512, 'height': 512, 'crop': 'fill', 'gravity': 'face'}
            ]
        )
        
        cloudinary_url = result.get('secure_url')
        print(f"✅ Uploaded to Cloudinary: {cloudinary_url}")
        
        # Save URL to BOTH working data AND persistent profile pictures mapping
        # 1. Update working synthetic_engagement.json
        data_file = os.path.join('data', 'synthetic_engagement.json')
        with open(data_file, 'r') as f:
            profiles = json.load(f)
        
        for profile in profiles:
            if profile.get('Name') == person_name:
                profile['profile_picture_url'] = cloudinary_url
                break
        
        with open(data_file, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        # 2. Update persistent profile_pictures.json (tracked in git)
        profile_pics_file = os.path.join('data', 'profile_pictures.json')
        try:
            with open(profile_pics_file, 'r') as f:
                profile_pics_mapping = json.load(f)
        except:
            profile_pics_mapping = {}
        
        profile_pics_mapping[person_name] = cloudinary_url
        
        with open(profile_pics_file, 'w') as f:
            json.dump(profile_pics_mapping, f, indent=2)
        
        print(f"💾 Saved to profile_pictures.json: {person_name} -> {cloudinary_url}")
        
        return jsonify({
            'success': True,
            'message': f'Profile picture uploaded for {person_name}!',
            'cloudinary_url': cloudinary_url
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Upload error: {error_details}")
        return jsonify({'success': False, 'error': str(e), 'details': error_details}), 500

@app.route('/personalized-images')
def personalized_images_page():
    """Personalized Image Generation Dashboard"""
    if 'connected' not in session:
        return redirect(url_for('login'))
    
    return render_template('personalized_images.html')

@app.route('/api/personalized-images/generate', methods=['POST'])
def generate_personalized_image():
    """Generate a personalized image for an individual"""
    try:
        data = request.get_json()
        individual_id = data.get('individual_id')
        custom_prompt = data.get('custom_prompt')
        
        print(f"🎨 API Request - Individual ID: {individual_id}")
        
        if not individual_id:
            return jsonify({'success': False, 'error': 'Individual ID required'}), 400
        
        # Load individual data
        engagement_file = 'data/synthetic_engagement.json'
        insights_file = 'data/individual_insights.json'
        
        with open(engagement_file, 'r') as f:
            engagement_data = json.load(f)
        
        # Find the individual
        individual = None
        for item in engagement_data:
            if item.get('id') == individual_id:
                individual = item
                break
        
        if not individual:
            print(f"❌ Individual not found: {individual_id}")
            return jsonify({'success': False, 'error': 'Individual not found'}), 404
        
        print(f"✅ Found individual: {individual.get('Name')}")
        
        # Load latest insights for this individual
        promotional_messages = []
        try:
            with open(insights_file, 'r') as f:
                insights_data = json.load(f)
            
            # Get ALL insights for this individual (sorted by timestamp)
            individual_insights = sorted(
                [i for i in insights_data if i.get('Individual_Id') == individual_id],
                key=lambda x: x.get('Event_Timestamp', ''),
                reverse=True
            )
            
            if individual_insights:
                latest_insight = individual_insights[0]  # Most recent
                individual['fitness_milestone'] = latest_insight.get('Fitness_Milestone')
                individual['favourite_brand'] = latest_insight.get('Favourite_Brand')
                individual['favourite_destination'] = latest_insight.get('Favourite_Destination')
                individual['hobby'] = latest_insight.get('Hobby')
                individual['lifestyle_quotient'] = latest_insight.get('Lifestyle_Quotient')
                individual['current_sentiment'] = latest_insight.get('Current_Sentiment')
                individual['favourite_exercise'] = latest_insight.get('Favourite_Exercise', 'Treadmill Running')
                individual['health_profile'] = latest_insight.get('Health_Profile')
                
                print(f"📊 Loaded insights: {latest_insight.get('Hobby')} + {latest_insight.get('Favourite_Brand')} + {latest_insight.get('Favourite_Exercise')}")
                
                # Check for Health Profile alerts
                if latest_insight.get('Health_Profile') == 'Hypertensive':
                    promotional_messages.append({
                        'type': 'health_alert',
                        'icon': '⚕️',
                        'title': 'Health Check Recommended',
                        'message': f"Based on your health profile, we recommend scheduling a consultation with a healthcare provider. Your wellbeing is our priority!",
                        'cta': 'Find a Doctor',
                        'priority': 'high'
                    })
                
                # Check for fitness milestone progression (offer 50% discount)
                previous_milestone = None
                if len(individual_insights) >= 2:
                    previous_insight = individual_insights[1]
                    current_milestone = latest_insight.get('Fitness_Milestone')
                    previous_milestone = previous_insight.get('Fitness_Milestone')
                    
                    milestone_order = ['Beginner', 'Intermediate', 'Advanced', 'Elite']
                    
                    if (current_milestone in milestone_order and 
                        previous_milestone in milestone_order and
                        milestone_order.index(current_milestone) > milestone_order.index(previous_milestone)):
                        
                        promotional_messages.append({
                            'type': 'milestone_offer',
                            'icon': '🎉',
                            'title': 'Congratulations on Your Progress!',
                            'message': f"You've advanced from {previous_milestone} to {current_milestone}! Celebrate with 50% OFF Premium Membership for 3 months.",
                            'cta': 'Claim Your Offer',
                            'discount': '50%',
                            'priority': 'high'
                        })
                        print(f"🎉 Milestone progression detected: {previous_milestone} → {current_milestone}")
                
                # Pass previous milestone to individual_data for image overlay
                if previous_milestone:
                    individual['previous_milestone'] = previous_milestone
                
                # Also pass Imminent_Event for link detection
                individual['imminent_event'] = latest_insight.get('Imminent_Event', '')
                
                individual['promotional_messages'] = promotional_messages
                
        except Exception as insights_error:
            print(f"⚠️ Could not load insights: {insights_error}")
            pass  # Use defaults if insights not available
        
        # Generate personalized image
        print(f"🚀 Starting image generation...")
        result = image_generator.generate_personalized_image(individual, custom_prompt)
        print(f"✅ Generation complete: {result.get('success')}")
        
        # Add promotional messages to result
        if promotional_messages:
            result['promotional_messages'] = promotional_messages
            print(f"💰 Added {len(promotional_messages)} promotional messages")
        
        # Add ALL insights to result for frontend display
        if individual_insights:
            latest_insight = individual_insights[0]
            result['insights'] = {
                'Favourite_Exercise': latest_insight.get('Favourite_Exercise', 'N/A'),
                'Favourite_Brand': latest_insight.get('Favourite_Brand', 'N/A'),
                'Favourite_Destination': latest_insight.get('Favourite_Destination', 'N/A'),
                'Hobby': latest_insight.get('Hobby', 'N/A'),
                'Lifestyle_Quotient': latest_insight.get('Lifestyle_Quotient', 'N/A'),
                'Current_Sentiment': latest_insight.get('Current_Sentiment', 'N/A'),
                'Health_Profile': latest_insight.get('Health_Profile', 'N/A'),
                'Fitness_Milestone': latest_insight.get('Fitness_Milestone', 'N/A'),
                'Purchase_Intent': latest_insight.get('Purchase_Intent', 'N/A'),
                'Imminent_Event': latest_insight.get('Imminent_Event', 'None')
            }
            print(f"📊 Added complete insights to result")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERROR in generate_personalized_image:")
        print(error_details)
        return jsonify({'success': False, 'error': str(e), 'details': error_details}), 500

@app.route('/api/personalized-images/batch', methods=['POST'])
def generate_batch_images():
    """Generate personalized images for a batch of individuals"""
    try:
        data = request.get_json()
        individual_ids = data.get('individual_ids', [])
        max_images = data.get('max_images', 10)
        
        if not individual_ids:
            return jsonify({'success': False, 'error': 'Individual IDs required'}), 400
        
        # Load data
        engagement_file = 'data/synthetic_engagement.json'
        with open(engagement_file, 'r') as f:
            engagement_data = json.load(f)
        
        # Filter individuals
        individuals = [item for item in engagement_data if item.get('id') in individual_ids]
        
        # Generate images
        results = image_generator.generate_campaign_batch({}, individuals, max_images)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personalized-images/scenarios/<individual_id>')
def get_scenario_suggestions(individual_id):
    """Get scenario suggestions for an individual"""
    try:
        # Load individual data
        engagement_file = 'data/synthetic_engagement.json'
        with open(engagement_file, 'r') as f:
            engagement_data = json.load(f)
        
        individual = None
        for item in engagement_data:
            if item.get('id') == individual_id:
                individual = item
                break
        
        if not individual:
            return jsonify({'success': False, 'error': 'Individual not found'}), 404
        
        suggestions = image_generator.get_scenario_suggestions(individual)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile-pictures/export')
def export_profile_pictures():
    """Export current profile picture URLs (for committing to git)"""
    try:
        profile_pics_file = os.path.join('data', 'profile_pictures.json')
        with open(profile_pics_file, 'r') as f:
            profile_pics = json.load(f)
        
        return jsonify({
            'success': True,
            'profile_pictures': profile_pics,
            'instructions': 'Copy this JSON and update data/profile_pictures.json in your local repo, then commit and push'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personalized-content/send-test-emails', methods=['POST'])
def send_personalized_content_emails():
    """Send personalized content emails for 5 segment members to test addresses"""
    try:
        # Test email recipients
        test_emails = [
            "bbanerjee@salesforce.com",
            "ursonly_rup@yahoo.co.uk"
        ]
        
        # The 5 segment members
        segment_members = [
            "Biswarup Banerjee",
            "Ashish Desai",
            "Deepika Chauhan",
            "Rajesh Rao",
            "Archana Tripathi"
        ]
        
        # Load data
        engagement_file = 'data/synthetic_engagement.json'
        insights_file = 'data/individual_insights.json'
        
        with open(engagement_file, 'r') as f:
            engagement_data = json.load(f)
        
        with open(insights_file, 'r') as f:
            insights_data = json.load(f)
        
        results = []
        generated_htmls = []
        
        for member_name in segment_members:
            # Find individual
            individual = None
            for ind in engagement_data:
                if ind.get('Name') == member_name:
                    individual = ind
                    break
            
            if not individual:
                continue
            
            # Get latest insights
            individual_insights = sorted(
                [i for i in insights_data if i.get('Individual_Name') == member_name],
                key=lambda x: x.get('Event_Timestamp', ''),
                reverse=True
            )
            
            latest_insight = individual_insights[0] if individual_insights else {}
            
            # Merge insights
            individual['fitness_milestone'] = latest_insight.get('Fitness_Milestone')
            individual['favourite_brand'] = latest_insight.get('Favourite_Brand')
            individual['favourite_destination'] = latest_insight.get('Favourite_Destination')
            individual['hobby'] = latest_insight.get('Hobby')
            individual['favourite_exercise'] = latest_insight.get('Favourite_Exercise', 'Treadmill Running')
            individual['health_profile'] = latest_insight.get('Health_Profile')
            individual['imminent_event'] = latest_insight.get('Imminent_Event', '')
            
            # Generate image and ensure it's stored in Cloudinary for email embedding
            print(f"🎨 Generating image for {member_name}...")
            image_result = image_generator.generate_personalized_image(individual)
            
            # Get image URL - should already be a Cloudinary URL
            image_url = image_result.get('image_url') if image_result.get('success') else individual.get('profile_picture_url', '')
            
            # Ensure image is stored in Cloudinary with proper naming for email embedding
            if image_url and image_result.get('success'):
                # Image is already in Cloudinary (from personalized_image_generator.py)
                # Store it with a specific naming convention for email use
                try:
                    import cloudinary
                    import cloudinary.uploader
                    import requests
                    from io import BytesIO
                    
                    cloudinary.config(
                        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
                        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
                        api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
                    )
                    
                    # If image is already a Cloudinary URL, use it directly
                    if 'res.cloudinary.com' in image_url:
                        print(f"✅ Image already in Cloudinary: {image_url[:100]}...")
                    else:
                        # Download and re-upload to Cloudinary with email-specific folder
                        print(f"📥 Downloading image to store in Cloudinary...")
                        img_response = requests.get(image_url, timeout=30)
                        if img_response.status_code == 200:
                            result = cloudinary.uploader.upload(
                                BytesIO(img_response.content),
                                folder="personalized_images_email",
                                public_id=f"email_{member_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                                overwrite=True,
                                resource_type="image"
                            )
                            image_url = result.get('secure_url')
                            print(f"✅ Stored in Cloudinary for email: {image_url[:100]}...")
                except Exception as e:
                    print(f"⚠️ Could not store image in Cloudinary: {e}, using original URL")
            
            # Generate email content
            engagement_score = float(individual.get('engagement_score', individual.get('omnichannel_score', 5.0)))
            vip_status = "VIP" if engagement_score >= 6.0 else "Standard"
            vip_label = "🌟 Exceptional VIP Member" if engagement_score >= 7.0 else "⭐ Premium VIP Member" if engagement_score >= 6.0 else "Valued Member"
            
            first_name = individual['Name'].split()[0]
            salutation = f"🌟 Dear {first_name},<br><br>As one of our <strong>{vip_label}</strong>, we're thrilled to bring you exclusive personalized content!" if vip_status == "VIP" else f"Dear {first_name},<br><br>Thank you for being a valued member!"
            
            preferred_channel = individual.get('preferred_channel', 'Email')
            
            # Build offers
            offers_html = ""
            if latest_insight.get('Fitness_Milestone') in ['Advanced', 'Elite']:
                offers_html += f'<div style="background: #f5f7fa; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea;"><strong>🎉 {latest_insight.get("Fitness_Milestone")} Premium Subscription - 50% OFF</strong><br>Celebrate your fitness level with our premium subscription!</div>'
            
            if latest_insight.get('Favourite_Brand'):
                offers_html += f'<div style="background: #f5f7fa; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea;"><strong>🏷️ Exclusive {latest_insight.get("Favourite_Brand")} Collection</strong><br>Special access with member-only pricing!</div>'
            
            # Vacation/flight offer
            if latest_insight.get('Imminent_Event') and 'vacation' in str(latest_insight.get('Imminent_Event', '')).lower():
                offers_html += f'<div style="background: #f5f7fa; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea;"><strong>✈️ Flight Booking Special - 15% OFF</strong><br>Book your flights to {latest_insight.get("Favourite_Destination", "your destination")} with exclusive member rates!</div>'
            
            # Guitar hobby offer
            if latest_insight.get('Hobby') and 'guitar' in str(latest_insight.get('Hobby', '')).lower():
                offers_html += f'<div style="background: #f5f7fa; padding: 15px; margin: 10px 0; border-left: 4px solid #667eea;"><strong>🎸 Guitar Purchase - 30% Discount</strong><br>Special discount on premium guitars for music enthusiasts!</div>'
            
            # Ensure image URL is absolute and from Cloudinary for email embedding
            if image_url and not image_url.startswith('http'):
                # If relative URL, make it absolute
                image_url = f"https://res.cloudinary.com/{os.environ.get('CLOUDINARY_CLOUD_NAME', 'demo')}/image/upload/{image_url}"
            
            # Build HTML email with proper structure for email clients
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personalized Content for {individual['Name']}</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="margin: 0; color: white;">🎯 Personalized Content for {individual['Name']}</h1>
        <div style="background: gold; color: #333; padding: 8px 20px; border-radius: 25px; display: inline-block; margin: 10px 0; font-weight: bold;">{vip_label}</div>
        <p style="margin: 10px 0 0 0;">Engagement Score: {engagement_score:.2f} | Preferred Channel: {preferred_channel}</p>
    </div>
    <div style="background: white; padding: 30px; border: 1px solid #e0e0e0;">
        <div style="font-size: 16px; margin-bottom: 20px; line-height: 1.6;">
            {salutation}
        </div>
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 30px;">🎁 Exclusive Offers</h2>
        {offers_html if offers_html else '<p>Check back soon for exclusive offers!</p>'}
        <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 30px;">🎨 Your Personalized Image</h2>
        <div style="text-align: center; margin: 20px 0;">
            <img src="{image_url}" alt="Personalized Content" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" />
        </div>
        <p style="color: #666; font-size: 12px; text-align: center; margin-top: 10px;">
            <em>💡 Tip: Generate personalized AI images via the "🎨 AI Personalized Images" page for full customization!</em>
        </p>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #667eea; margin-top: 0;">📊 Your Profile</h3>
            <p style="margin: 8px 0;"><strong>Exercise:</strong> {latest_insight.get('Favourite_Exercise', 'N/A')}</p>
            <p style="margin: 8px 0;"><strong>Brand:</strong> {latest_insight.get('Favourite_Brand', 'N/A')}</p>
            <p style="margin: 8px 0;"><strong>Destination:</strong> {latest_insight.get('Favourite_Destination', 'N/A')}</p>
            <p style="margin: 8px 0;"><strong>Milestone:</strong> {latest_insight.get('Fitness_Milestone', 'N/A')}</p>
            <p style="margin: 8px 0;"><strong>Health Profile:</strong> {latest_insight.get('Health_Profile', 'N/A')}</p>
        </div>
    </div>
    <div style="background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px;">
        <p style="margin: 0;">This is a test email sent for demonstration purposes.</p>
    </div>
</body>
</html>"""
            
            # Save HTML for preview
            os.makedirs('generated_emails', exist_ok=True)
            html_file = f"generated_emails/email_{member_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_file, 'w') as f:
                f.write(html_content)
            generated_htmls.append(html_file)
            
            # Send emails via Salesforce if connected
            subject = f"🎯 Personalized Content for {member_name} - {vip_label} ({preferred_channel})"
            
            for test_email in test_emails:
                try:
                    if not sf_manager.is_connected():
                        results.append({
                            'recipient': test_email,
                            'individual': member_name,
                            'status': 'pending',
                            'message': 'Salesforce not connected - HTML file generated',
                            'html_file': html_file,
                            'subject': subject
                        })
                        continue
                    
                    # Use Salesforce Email API - try multiple methods for HTML rendering
                    # Method 1: Use Apex SingleEmailMessage (most reliable for HTML)
                    try:
                        # Properly escape HTML for Apex string
                        html_escaped = html_content.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
                        subject_escaped = subject.replace("'", "\\'")
                        
                        apex_code = f"""
                        Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
                        email.setToAddresses(new String[] {{'{test_email}'}});
                        email.setSubject('{subject_escaped}');
                        email.setHtmlBody('{html_escaped}');
                        email.setSaveAsActivity(false);
                        Messaging.SendEmailResult[] results = Messaging.sendEmail(new Messaging.SingleEmailMessage[] {{ email }});
                        System.debug('Email sent: ' + results[0].isSuccess());
                        """
                        
                        result = sf_manager.sf.toolingexecuteanonymous(apex_code)
                        if not result.get('success'):
                            error_msg = result.get('compileProblem') or result.get('exceptionMessage', 'Unknown error')
                            raise Exception(f"Apex execution failed: {error_msg}")
                        print(f"✅ Email sent successfully via Apex SingleEmailMessage (HTML)")
                    except Exception as apex_error:
                        # Method 2: Fallback to emailSimple API with explicit HTML format
                        print(f"⚠️ Apex method failed: {apex_error}, trying emailSimple API...")
                        try:
                            email_payload = {
                                "inputs": [{
                                    "emailAddresses": test_email,
                                    "emailSubject": f"[TEST] {subject}",
                                    "emailBody": html_content,
                                    "emailFormat": "Html",
                                    "senderType": "CurrentUser"
                                }]
                            }
                            result = sf_manager.sf.restful(
                                'actions/standard/emailSimple',
                                method='POST',
                                data=json.dumps(email_payload),
                                headers={'Content-Type': 'application/json'}
                            )
                            print(f"✅ Email sent via emailSimple API")
                        except Exception as email_simple_error:
                            # Method 3: Last resort - save HTML file and provide link
                            print(f"⚠️ emailSimple also failed: {email_simple_error}")
                            raise Exception(f"All email methods failed. HTML saved to: {html_file}. Last error: {email_simple_error}")
                    
                    results.append({
                        'recipient': test_email,
                        'individual': member_name,
                        'status': 'sent',
                        'subject': subject,
                        'html_file': html_file
                    })
                    
                except Exception as e:
                    results.append({
                        'recipient': test_email,
                        'individual': member_name,
                        'status': 'failed',
                        'error': str(e),
                        'html_file': html_file
                    })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_sent': len([r for r in results if r['status'] == 'sent']),
            'total_failed': len([r for r in results if r['status'] == 'failed']),
            'total_pending': len([r for r in results if r['status'] == 'pending']),
            'html_files': generated_htmls,
            'message': 'Check generated_emails/ folder for HTML previews' if not sf_manager.is_connected() else 'Emails sent successfully'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'connected': sf_manager.is_connected()
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Get port from environment variable (for Heroku) or use 5001 for local
    port = int(os.environ.get('PORT', 5001))
    
    # Determine if running in production (Heroku sets PORT env var)
    is_production = 'PORT' in os.environ
    
    print("="*80)
    print("DATA CLOUD MANAGEMENT APPLICATION")
    print("="*80)
    print(f"\n🚀 Starting server...")
    
    if is_production:
        print(f"🌐 Environment: PRODUCTION")
        print(f"📍 Port: {port}")
    else:
        print(f"🖥️  Environment: DEVELOPMENT")
        print(f"📍 URL: http://localhost:{port}")
        print(f"📖 API Docs: http://localhost:{port}/api/docs")
    
    print("\n" + "="*80)
    
    # Run with debug=False in production, debug=True in development
    app.run(debug=not is_production, host='0.0.0.0', port=port)

