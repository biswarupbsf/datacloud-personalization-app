"""
Segmentation Engine
Creates and manages segments based on filters
"""

import json
import os
from datetime import datetime
import uuid

class SegmentationEngine:
    
    def __init__(self):
        self.segments_file = 'data/segments.json'
        self.engagement_file = 'data/synthetic_engagement.json'  # Using synthetic data with email + website
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.segments_file):
            with open(self.segments_file, 'w') as f:
                json.dump([], f)
    
    def list_segments(self):
        """List all saved segments"""
        try:
            with open(self.segments_file, 'r') as f:
                segments = json.load(f)
            return segments
        except:
            return []
    
    def create_segment(self, sf, name, description, base_object, filters):
        """Create a new segment"""
        segment_id = str(uuid.uuid4())
        
        # Check if filters include engagement fields (email + website + messages)
        engagement_fields = [
            'engagement_score', 'omnichannel_score',
            'email_opens', 'email_clicks', 'email_bounces', 'email_unsubscribes',
            'website_product_views', 'website_add_to_cart', 'website_cart_abandons', 'website_purchases',
            'total_order_value',
            'sms_sends', 'sms_opens', 'sms_clicks', 'sms_optouts', 'sms_open_rate',
            'whatsapp_sends', 'whatsapp_reads', 'whatsapp_replies', 'whatsapp_optouts', 'whatsapp_read_rate',
            'push_sends', 'push_opens', 'push_clicks', 'push_open_rate',
            'total_message_sends', 'total_message_interactions', 'preferred_channel'
        ]
        engagement_filters = [f for f in filters if f.get('field') in engagement_fields]
        has_engagement_filters = len(engagement_filters) > 0
        
        if has_engagement_filters and base_object == 'Individual':
            # Use engagement data to filter
            members = self._get_members_with_engagement(sf, filters)
            member_count = len(members)
            query = f"Engagement-based segment: {len(engagement_filters)} engagement filter(s)"
        else:
            # Execute standard SOQL query
            query = self._build_query(base_object, filters)
            results = sf.query(query)
            member_count = results['totalSize']
        
        segment = {
            'id': segment_id,
            'name': name,
            'description': description,
            'base_object': base_object,
            'filters': filters,
            'member_count': member_count,
            'created_at': datetime.now().isoformat(),
            'query': query,
            'salesforce_campaign_id': None,
            'uses_engagement': has_engagement_filters
        }
        
        # Save segment
        segments = self.list_segments()
        segments.append(segment)
        
        with open(self.segments_file, 'w') as f:
            json.dump(segments, f, indent=2)
        
        return segment
    
    def get_segment_members(self, sf, segment_id):
        """Get members of a segment"""
        segments = self.list_segments()
        segment = next((s for s in segments if s['id'] == segment_id), None)
        
        if not segment:
            raise Exception("Segment not found")
        
        # Check if this is a driving segment (members stored directly)
        if segment.get('type') == 'driving':
            members = segment.get('members', [])
            return {
                'segment': segment,
                'members': members,
                'totalSize': len(members)
            }
        
        # Check if this is an engagement-based segment
        if segment.get('uses_engagement', False):
            members = self._get_members_with_engagement(sf, segment['filters'])
            
            # Apply purchase intent filter if specified
            if segment.get('purchase_intent_filter'):
                members = [m for m in members if m.get('Purchase_Intent') in segment.get('purchase_intent_filter')]
            
            # Apply sentiment filter if specified
            if segment.get('sentiment_filter'):
                members = [m for m in members if m.get('Current_Sentiment') in segment.get('sentiment_filter')]
            
            # Sort by omnichannel score
            members = sorted(members, key=lambda x: x.get('omnichannel_score', x.get('engagement_score', 0)), reverse=True)
            
            # Apply limit if specified in segment metadata
            if segment.get('limit') and len(members) > segment['limit']:
                members = members[:segment['limit']]
            
            return {
                'segment': segment,
                'members': members,
                'totalSize': len(members)
            }
        else:
            # Execute standard query
            results = sf.query(segment['query'])
            members = results['records']
            
            # Apply limit if specified in segment metadata
            if segment.get('limit') and len(members) > segment['limit']:
                members = members[:segment['limit']]
            
            return {
                'segment': segment,
                'members': members,
                'totalSize': len(members)
            }
    
    def preview_segment(self, sf, base_object, filters):
        """Preview segment results"""
        query = self._build_query(base_object, filters, limit=100)
        results = sf.query(query)
        
        return results['records']
    
    def sync_to_campaign(self, sf, segment_id):
        """Sync segment to Salesforce Campaign"""
        segment_data = self.get_segment_members(sf, segment_id)
        segment = segment_data['segment']
        members = segment_data['members']
        
        # Create Campaign
        campaign_data = {
            'Name': segment['name'],
            'Description': segment['description'],
            'Status': 'Planned',
            'Type': 'Email',
            'IsActive': True
        }
        
        campaign_result = sf.Campaign.create(campaign_data)
        campaign_id = campaign_result['id']
        
        # Update segment with campaign ID
        segments = self.list_segments()
        for seg in segments:
            if seg['id'] == segment_id:
                seg['salesforce_campaign_id'] = campaign_id
                break
        
        with open(self.segments_file, 'w') as f:
            json.dump(segments, f, indent=2)
        
        return {
            'campaign_id': campaign_id,
            'name': segment['name'],
            'member_count': len(members)
        }
    
    def _build_query(self, base_object, filters, limit=None):
        """Build SOQL query from filters"""
        # Get object fields
        fields = ['Id', 'Name']
        
        # Build WHERE clause
        where_clauses = []
        for f in filters:
            field = f['field']
            operator = f['operator']
            value = f['value']
            
            if operator == 'equals':
                if isinstance(value, str):
                    where_clauses.append(f"{field} = '{value}'")
                else:
                    where_clauses.append(f"{field} = {value}")
            elif operator == 'not_equals':
                if isinstance(value, str):
                    where_clauses.append(f"{field} != '{value}'")
                else:
                    where_clauses.append(f"{field} != {value}")
            elif operator == 'greater_than':
                where_clauses.append(f"{field} > {value}")
            elif operator == 'less_than':
                where_clauses.append(f"{field} < {value}")
            elif operator == 'contains':
                where_clauses.append(f"{field} LIKE '%{value}%'")
            elif operator == 'starts_with':
                where_clauses.append(f"{field} LIKE '{value}%'")
        
        # Build query
        query = f"SELECT {', '.join(fields)} FROM {base_object}"
        
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return query
    
    def get_segment_analytics(self, sf):
        """Get analytics for all segments"""
        segments = self.list_segments()
        
        analytics = {
            'total_segments': len(segments),
            'total_members': sum(s.get('member_count', 0) for s in segments),
            'synced_campaigns': sum(1 for s in segments if s.get('salesforce_campaign_id')),
            'segments_by_object': {}
        }
        
        # Group by object
        for seg in segments:
            obj = seg['base_object']
            if obj not in analytics['segments_by_object']:
                analytics['segments_by_object'][obj] = 0
            analytics['segments_by_object'][obj] += 1
        
        return analytics
    
    def _get_members_with_engagement(self, sf, filters):
        """Get Individual records with engagement data applied"""
        # Load engagement data
        try:
            with open(self.engagement_file, 'r') as f:
                engagement_data = json.load(f)
        except FileNotFoundError:
            raise Exception("Engagement data not found. Please run add_engagement_scores.py first.")
        
        # Load insights data for purchase intent and sentiment filtering
        insights_by_id = {}
        try:
            insights_file = 'data/individual_insights.json'
            with open(insights_file, 'r') as f:
                insights_data = json.load(f)
            
            # Create lookup by Individual_Id - get the most recent insight for each individual
            for insight in insights_data:
                ind_id = insight.get('Individual_Id')
                if ind_id:
                    insights_by_id[ind_id] = insight
        except Exception as e:
            print(f"Warning: Could not load insights data: {e}")
        
        # Get all Individuals
        query = "SELECT Id, Name FROM Individual"
        individuals = sf.query(query)['records']
        
        # Create lookup dict
        engagement_lookup = {e['id']: e for e in engagement_data}
        
        # Merge engagement data with Salesforce records
        members = []
        for ind in individuals:
            eng_data = engagement_lookup.get(ind['Id'])
            if eng_data:
                # Merge the data (omnichannel: email + website + messages)
                # Use Name from engagement data (real names) instead of Salesforce (Test Person names)
                merged = {
                    'Id': ind['Id'],
                    'Name': eng_data.get('Name', ind['Name']),  # Prefer engagement data Name
                    'engagement_score': eng_data.get('engagement_score', 0),
                    'omnichannel_score': eng_data.get('omnichannel_score', 0),
                    # Email engagement
                    'email_opens': eng_data.get('email_opens', 0),
                    'email_clicks': eng_data.get('email_clicks', 0),
                    'email_bounces': eng_data.get('email_bounces', 0),
                    'email_unsubscribes': eng_data.get('email_unsubscribes', 0),
                    # Website engagement
                    'website_product_views': eng_data.get('website_product_views', 0),
                    'website_add_to_cart': eng_data.get('website_add_to_cart', 0),
                    'website_cart_abandons': eng_data.get('website_cart_abandons', 0),
                    'website_purchases': eng_data.get('website_purchases', 0),
                    'total_order_value': eng_data.get('total_order_value', 0.0),
                    # SMS engagement
                    'sms_sends': eng_data.get('sms_sends', 0),
                    'sms_opens': eng_data.get('sms_opens', 0),
                    'sms_clicks': eng_data.get('sms_clicks', 0),
                    'sms_optouts': eng_data.get('sms_optouts', 0),
                    'sms_open_rate': eng_data.get('sms_open_rate', 0),
                    # WhatsApp engagement
                    'whatsapp_sends': eng_data.get('whatsapp_sends', 0),
                    'whatsapp_reads': eng_data.get('whatsapp_reads', 0),
                    'whatsapp_replies': eng_data.get('whatsapp_replies', 0),
                    'whatsapp_optouts': eng_data.get('whatsapp_optouts', 0),
                    'whatsapp_read_rate': eng_data.get('whatsapp_read_rate', 0),
                    # Push notifications
                    'push_sends': eng_data.get('push_sends', 0),
                    'push_opens': eng_data.get('push_opens', 0),
                    'push_clicks': eng_data.get('push_clicks', 0),
                    'push_open_rate': eng_data.get('push_open_rate', 0),
                    # Combined message metrics
                    'total_message_sends': eng_data.get('total_message_sends', 0),
                    'total_message_interactions': eng_data.get('total_message_interactions', 0),
                    'preferred_channel': eng_data.get('preferred_channel', ''),
                    # Other fields
                    'products_browsed': ', '.join(eng_data.get('products_browsed', [])[:5]) if eng_data.get('products_browsed') else '',
                    'products_purchased': ', '.join(eng_data.get('products_purchased', [])[:5]) if eng_data.get('products_purchased') else '',
                    'favorite_category': eng_data.get('favorite_category', ''),
                    'last_engagement': eng_data.get('last_engagement_date', '')
                }
                
                # Add insights data if available (for purchase intent and sentiment filtering)
                if ind['Id'] in insights_by_id:
                    insight = insights_by_id[ind['Id']]
                    merged['Purchase_Intent'] = insight.get('Purchase_Intent', 'N/A')
                    merged['Current_Sentiment'] = insight.get('Current_Sentiment', 'N/A')
                    merged['Favourite_Brand'] = insight.get('Favourite_Brand', 'N/A')
                    merged['Lifestyle_Quotient'] = insight.get('Lifestyle_Quotient', 'N/A')
                    merged['Health_Profile'] = insight.get('Health_Profile', 'N/A')
                    merged['Imminent_Event'] = insight.get('Imminent_Event', '')
                    merged['FirstName'] = eng_data.get('FirstName', '')
                    merged['LastName'] = eng_data.get('LastName', '')
                else:
                    merged['Purchase_Intent'] = 'N/A'
                    merged['Current_Sentiment'] = 'N/A'
                    merged['Favourite_Brand'] = 'N/A'
                    merged['Lifestyle_Quotient'] = 'N/A'
                    merged['Health_Profile'] = 'N/A'
                    merged['Imminent_Event'] = ''
                    merged['FirstName'] = eng_data.get('FirstName', '')
                    merged['LastName'] = eng_data.get('LastName', '')
                
                members.append(merged)
        
        # Apply filters
        filtered_members = []
        for member in members:
            passes_all_filters = True
            for f in filters:
                field = f['field']
                operator = f['operator']
                value = f['value']
                
                # Convert value to number if it's a numeric field
                numeric_fields = [
                    'engagement_score', 'omnichannel_score',
                    'email_opens', 'email_clicks', 'email_bounces', 'email_unsubscribes',
                    'website_product_views', 'website_add_to_cart', 'website_cart_abandons', 'website_purchases',
                    'total_order_value',
                    'sms_sends', 'sms_opens', 'sms_clicks', 'sms_optouts', 'sms_open_rate',
                    'whatsapp_sends', 'whatsapp_reads', 'whatsapp_replies', 'whatsapp_optouts', 'whatsapp_read_rate',
                    'push_sends', 'push_opens', 'push_clicks', 'push_open_rate',
                    'total_message_sends', 'total_message_interactions'
                ]
                if field in numeric_fields:
                    try:
                        value = float(value)
                    except:
                        value = 0
                
                member_value = member.get(field)
                
                if operator == 'equals':
                    if member_value != value:
                        passes_all_filters = False
                        break
                elif operator == 'not_equals':
                    if member_value == value:
                        passes_all_filters = False
                        break
                elif operator == 'greater_than':
                    if member_value <= value:
                        passes_all_filters = False
                        break
                elif operator == 'greater_than_or_equal':
                    if member_value < value:
                        passes_all_filters = False
                        break
                elif operator == 'less_than':
                    if member_value >= value:
                        passes_all_filters = False
                        break
                elif operator == 'less_than_or_equal':
                    if member_value > value:
                        passes_all_filters = False
                        break
                elif operator == 'contains':
                    if value not in str(member_value):
                        passes_all_filters = False
                        break
            
            if passes_all_filters:
                filtered_members.append(member)
        
        # Sort by engagement_score descending
        filtered_members.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
        
        # Check if there's a limit in the description or filters
        # For "top N" segments, we'll take just the first N
        # This is a simple heuristic - you could make it more sophisticated
        
        return filtered_members

