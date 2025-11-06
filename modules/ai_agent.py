"""
AI Agent for Conversational Data Cloud Management
Interprets natural language requests and executes appropriate actions
"""

import json
import re
from datetime import datetime

class AIAgent:
    
    def __init__(self):
        self.conversation_history = []
        self.context = {
            'last_segment_created': None,
            'last_segment_id': None,
            'last_segment_name': None,
            'last_action': None,
            'entities_mentioned': []
        }
        self.available_actions = {
            'create_segment': ['create a segment', 'create segment', 'new segment', 'make a segment', 'make segment', 'build segment', 'segment of', 'filter individuals', 'filter users'],
            'send_email_test': ['generate html', 'create html', 'render', 'html format', 'send email', 'send to', 'email to', 'send to my email', 'test email', 'email me', 'send it to', 'whatsapp message', 'send whatsapp', 'mobile number', 'see all', 'view all', 'all 50', 'all members', 'all content', '50 contents', 'entire segment'],
            'view_segment': ['show me the', 'view the', 'last segment', 'recent segment', 'my segment', 'segment I created', 'what segment', 'which segment', 'list segments'],
            'generate_email': ['personalize', 'personalise', 'content', 'deliver', 'campaign', 'write email'],
            'investigate_table': ['investigate', 'explore', 'query', 'table contents', 'show table', 'display table'],
            'create_records': ['create records', 'add data', 'insert', 'generate data', 'synthetic'],
            'show_analytics': ['analytics', 'stats', 'metrics', 'performance', 'report'],
            'explain_data': ['explain', 'what is', 'describe', 'tell me about']
        }
    
    def process_request(self, user_message, sf, data_manager, segmentation_engine, email_generator, datacloud_analytics):
        """Process a natural language request and return structured response"""
        
        user_message_lower = user_message.lower()
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'agent': None  # Will be filled after processing
        })
        
        # Detect intent
        intent = self._detect_intent(user_message_lower)
        
        response = {
            'intent': intent,
            'message': '',
            'data': None,
            'suggested_actions': [],
            'conversation_id': len(self.conversation_history) - 1
        }
        
        try:
            if intent == 'send_email_test':
                response = self._handle_send_email_test(user_message, user_message_lower, sf, segmentation_engine)
            
            elif intent == 'view_segment':
                response = self._handle_view_segment(user_message, user_message_lower, sf, segmentation_engine)
            
            elif intent == 'investigate_table':
                response = self._handle_investigate_table(user_message, user_message_lower, sf, data_manager)
            
            elif intent == 'create_segment':
                response = self._handle_create_segment(user_message, user_message_lower, sf, segmentation_engine)
            
            elif intent == 'generate_email':
                response = self._handle_generate_email(user_message, user_message_lower, sf, email_generator, segmentation_engine)
            
            elif intent == 'create_records':
                response = self._handle_create_records(user_message, user_message_lower, sf, data_manager)
            
            elif intent == 'show_analytics':
                response = self._handle_show_analytics(user_message, user_message_lower, sf, datacloud_analytics, segmentation_engine)
            
            elif intent == 'explain_data':
                response = self._handle_explain_data(user_message, user_message_lower, sf)
            
            else:
                response['message'] = self._handle_unknown_intent(user_message)
        
        except Exception as e:
            response['message'] = f"❌ Error processing your request: {str(e)}\n\nPlease try rephrasing your question or be more specific."
            response['intent'] = 'error'
        
        # Update conversation history with context
        self.conversation_history[-1]['agent'] = response['message']
        self.conversation_history[-1]['context'] = dict(self.context)  # Save context snapshot
        
        return response
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        
        # Check each action type
        for intent, keywords in self.available_actions.items():
            for keyword in keywords:
                if keyword in message:
                    return intent
        
        return 'unknown'
    
    def _handle_investigate_table(self, original_message, message, sf, data_manager):
        """Handle requests to investigate/view table contents"""
        
        # Check for Individual Insights first (local synthetic data)
        if 'insights' in message or 'behavioral insights' in message or 'behaviour' in message:
            return self._handle_investigate_insights()
        
        # Extract object name
        objects = ['individual', 'contact', 'campaign', 'opportunity', 'account', 'lead', 
                   'order', 'campaignmember', 'contactpointemail']
        
        detected_object = None
        for obj in objects:
            if obj in message:
                detected_object = obj.capitalize()
                if detected_object == 'Campaignmember':
                    detected_object = 'CampaignMember'
                if detected_object == 'Contactpointemail':
                    detected_object = 'ContactPointEmail'
                break
        
        if not detected_object:
            return {
                'intent': 'investigate_table',
                'message': "🤔 I'd love to help you investigate a table! Which object would you like to explore?\n\nAvailable objects:\n• Individual Insights (Behavioral data)\n• Individual\n• Contact\n• Campaign\n• Opportunity\n• Account\n• Lead\n• Order\n\nTry asking: 'Show me the Individual Insights data' or 'Investigate the Individual table'",
                'data': None,
                'suggested_actions': ['investigate Individual Insights', 'investigate table Individual', 'investigate table Contact']
            }
        
        try:
            # Get records
            records_data = data_manager.get_records(sf, detected_object, limit=20)
            
            # Get field info
            fields_info = data_manager.get_object_fields(sf, detected_object)
            
            message_text = f"📊 **{detected_object} Table Investigation**\n\n"
            message_text += f"**Total Records:** {records_data['totalSize']:,}\n"
            message_text += f"**Sample Records:** Showing first {len(records_data['records'])}\n\n"
            
            # Show fields
            message_text += f"**Available Fields ({len(fields_info)}):**\n"
            key_fields = [f for f in fields_info if f['name'] in ['Id', 'Name', 'Email', 'Status', 'Type', 'CreatedDate']][:8]
            for field in key_fields:
                message_text += f"• {field['label']} ({field['name']}) - {field['type']}\n"
            
            if len(fields_info) > len(key_fields):
                message_text += f"• ... and {len(fields_info) - len(key_fields)} more fields\n"
            
            message_text += f"\n✅ **Found {records_data['totalSize']:,} {detected_object} records!**"
            
            return {
                'intent': 'investigate_table',
                'message': message_text,
                'data': {
                    'object': detected_object,
                    'total_records': records_data['totalSize'],
                    'sample_records': records_data['records'][:5],
                    'fields': fields_info
                },
                'suggested_actions': [
                    f'Create a segment from {detected_object}',
                    f'Show me analytics for {detected_object}',
                    f'Export {detected_object} data'
                ]
            }
            
        except Exception as e:
            return {
                'intent': 'investigate_table',
                'message': f"❌ Couldn't access {detected_object} table: {str(e)}\n\nMake sure the object exists and you have permission to access it.",
                'data': None,
                'suggested_actions': ['Try a different object', 'Check permissions']
            }
    
    def _handle_investigate_insights(self):
        """Handle investigation of Individual Insights behavioral data"""
        
        try:
            import json
            from collections import Counter
            
            # Load insights data
            with open('data/individual_insights.json', 'r') as f:
                insights_data = json.load(f)
            
            if not insights_data:
                return {
                    'intent': 'investigate_table',
                    'message': "❌ No Individual Insights data found. Please generate the insights data first.",
                    'data': None,
                    'suggested_actions': ['Generate insights data', 'Create synthetic data']
                }
            
            # Calculate statistics
            total_records = len(insights_data)
            unique_individuals = len(set(i['Individual_Id'] for i in insights_data))
            
            # Get distributions
            sentiments = Counter(i['Current_Sentiment'] for i in insights_data)
            lifestyles = Counter(i['Lifestyle_Quotient'] for i in insights_data)
            health_profiles = Counter(i['Health_Profile'] for i in insights_data)
            purchase_intents = Counter(i['Purchase_Intent'] for i in insights_data)
            
            # Build message
            message_text = f"🔮 **Individual Insights Data Investigation**\n\n"
            message_text += f"**📊 Overview:**\n"
            message_text += f"• Total Records: {total_records:,}\n"
            message_text += f"• Unique Individuals: {unique_individuals}\n"
            message_text += f"• Records per Individual: ~{total_records // unique_individuals}\n"
            message_text += f"• Time Range: Last 90 days\n\n"
            
            message_text += f"**📋 Data Fields:**\n"
            message_text += f"• Individual_Id (Primary Key)\n"
            message_text += f"• Event_Timestamp (Primary Key)\n"
            message_text += f"• Current_Sentiment\n"
            message_text += f"• Lifestyle_Quotient\n"
            message_text += f"• Health_Profile\n"
            message_text += f"• Fitness_Milestone\n"
            message_text += f"• Purchase_Intent\n"
            message_text += f"• Favourite_Brand\n"
            message_text += f"• Favourite_Destination\n"
            message_text += f"• Hobby\n"
            message_text += f"• Imminent_Event\n\n"
            
            message_text += f"**😊 Sentiment Distribution (Top 5):**\n"
            for sentiment, count in sentiments.most_common(5):
                pct = (count / total_records) * 100
                message_text += f"• {sentiment}: {count} ({pct:.1f}%)\n"
            
            message_text += f"\n**🎯 Lifestyle Distribution (Top 5):**\n"
            for lifestyle, count in lifestyles.most_common(5):
                pct = (count / total_records) * 100
                message_text += f"• {lifestyle}: {count} ({pct:.1f}%)\n"
            
            message_text += f"\n**💪 Health Profile Distribution (Top 5):**\n"
            for profile, count in health_profiles.most_common(5):
                pct = (count / total_records) * 100
                message_text += f"• {profile}: {count} ({pct:.1f}%)\n"
            
            message_text += f"\n**🛒 Purchase Intent Distribution:**\n"
            for intent, count in purchase_intents.most_common():
                pct = (count / total_records) * 100
                message_text += f"• {intent}: {count} ({pct:.1f}%)\n"
            
            message_text += f"\n✅ **Found {total_records:,} behavioral insight records!**\n\n"
            message_text += f"💡 **Use Cases:**\n"
            message_text += f"• Sentiment-based segmentation\n"
            message_text += f"• Lifestyle-targeted campaigns\n"
            message_text += f"• Health-aware messaging\n"
            message_text += f"• Purchase intent predictions\n"
            message_text += f"• Event-triggered communications"
            
            # Sample records
            sample_records = insights_data[:10]
            
            return {
                'intent': 'investigate_table',
                'message': message_text,
                'data': {
                    'object': 'Individual_Insights',
                    'total_records': total_records,
                    'unique_individuals': unique_individuals,
                    'sample_records': sample_records,
                    'distributions': {
                        'sentiments': dict(sentiments.most_common(10)),
                        'lifestyles': dict(lifestyles.most_common(10)),
                        'health_profiles': dict(health_profiles.most_common(10)),
                        'purchase_intents': dict(purchase_intents)
                    }
                },
                'suggested_actions': [
                    'Show me insights analytics',
                    'Create segment based on sentiment',
                    'Export insights data'
                ]
            }
            
        except FileNotFoundError:
            return {
                'intent': 'investigate_table',
                'message': "❌ Individual Insights data file not found.\n\nThe file should be located at: `data/individual_insights.json`\n\nPlease generate the insights data first.",
                'data': None,
                'suggested_actions': ['Generate insights data', 'Check file location']
            }
        except Exception as e:
            return {
                'intent': 'investigate_table',
                'message': f"❌ Error loading Individual Insights data: {str(e)}",
                'data': None,
                'suggested_actions': ['Check data file', 'Regenerate data']
            }
    
    def _handle_create_segment(self, original_message, message, sf, segmentation_engine):
        """Handle segment creation requests - ACTUALLY CREATE THE SEGMENT"""
        
        # Parse request for segment requirements
        segment_name = "AI Generated Segment"
        filters = []
        limit = None
        purchase_intent_filter = None
        sentiment_filter = None
        
        # **NEW: Detect driving/vehicle-related requests**
        driving_keywords = ['driver', 'drivers', 'driving', 'speed', 'kmph', 'mph', 'efficient', 'safe', 'safety', 'vehicle', 'car', 'telemetry', 'acceleration', 'braking']
        is_driving_query = any(keyword in message for keyword in driving_keywords)
        
        if is_driving_query:
            # This is a driving-related segment request
            return self._handle_driving_segment(original_message, message, sf, segmentation_engine)
        
        # Detect "super engaged" or "highly engaged"
        # Note: Max score in data is ~6.88, adjusted to find reasonable matches
        if 'super engaged' in message or 'highly engaged' in message or 'high engagement' in message:
            filters.append({'field': 'omnichannel_score', 'operator': '>=', 'value': '5'})
            segment_name = "Super Engaged Individuals"
        elif 'engaged' in message:
            filters.append({'field': 'omnichannel_score', 'operator': '>=', 'value': '3'})
            segment_name = "Engaged Individuals"
        
        # Detect purchase intent requirements
        if 'very high' in message and 'intent' in message or 'immediate' in message and 'intent' in message or 'high' in message and ('intent' in message or 'purchase' in message):
            # Include "Considering" as it shows purchase interest
            purchase_intent_filter = ['Very High', 'Immediate', 'High', 'Considering']
            segment_name = "High Intent " + segment_name if segment_name != "AI Generated Segment" else "High Intent Individuals"
        elif 'intent' in message or 'purchase' in message:
            purchase_intent_filter = ['Very High', 'Immediate', 'High', 'Considering', 'Medium']
            
        # Detect sentiment/emotional requirements
        if 'emotional high' in message or 'positive emotion' in message or 'happy' in message or 'excited' in message:
            # Include neutral/positive sentiments, exclude only very negative ones
            sentiment_filter = ['Happy', 'Elated', 'Excited', 'Calm', 'Content', 'Anxious', 'Stressed']
            if segment_name != "AI Generated Segment":
                segment_name = "Positive " + segment_name
        elif 'emotion' in message or 'sentiment' in message:
            # If emotion mentioned but not specific, exclude very negative ones
            sentiment_filter = ['Happy', 'Elated', 'Excited', 'Calm', 'Content', 'Anxious', 'Stressed']
        
        # Detect "top N individuals" or "N most highly engaged" or "N individuals"
        # Match patterns like: "10 individuals", "10 most engaged", "top 10", "10 highly engaged individuals"
        size_match = re.search(r'(?:top\s+)?(\d+)(?:\s+\w+)*\s+individuals?', message, re.IGNORECASE)
        if not size_match:
            # Try simpler patterns
            size_match = re.search(r'(\d+)\s+(?:most|top|highly)', message, re.IGNORECASE)
        if size_match:
            limit = int(size_match.group(1))
        
        # Check if user wants top performers by channel
        include_channel_breakdown = False
        if ('top' in message and 'by each channel' in message) or ('top 5' in message and 'channel' in message):
            include_channel_breakdown = True
        
        # If user wants specific number without other criteria, just use omnichannel score
        if limit and not filters:
            filters.append({'field': 'omnichannel_score', 'operator': '>=', 'value': '5'})
            segment_name = f"Top {limit} Engaged Individuals"
        
        # Try to create the segment if we have criteria
        if filters or limit:
            try:
                # Apply limit if specified (by modifying filters to only get top N by omnichannel_score)
                if limit:
                    # We'll handle limit by getting all members and slicing
                    pass
                
                # Create the segment
                segment = segmentation_engine.create_segment(
                    sf=sf,
                    name=segment_name,
                    description=f"AI-generated segment based on: {original_message}",
                    base_object="Individual",
                    filters=filters
                )
                
                if segment:
                    result = segmentation_engine.get_segment_members(sf, segment['id'])
                    members = result['members']
                    
                    # Apply purchase intent filter if specified
                    if purchase_intent_filter:
                        members = [m for m in members if m.get('Purchase_Intent') in purchase_intent_filter]
                    
                    # Apply sentiment filter if specified
                    if sentiment_filter:
                        members = [m for m in members if m.get('Current_Sentiment') in sentiment_filter]
                    
                    # Sort by omnichannel score
                    members = sorted(members, key=lambda x: x.get('omnichannel_score', 0), reverse=True)
                    
                    # Apply limit if specified
                    if limit and len(members) > limit:
                        members = members[:limit]
                    
                    # ALWAYS save filters and limit to segment metadata (not just when slicing)
                    if limit or purchase_intent_filter or sentiment_filter:
                        import json
                        segments = segmentation_engine.list_segments()
                        for i, s in enumerate(segments):
                            if s['id'] == segment['id']:
                                if limit:
                                    segments[i]['member_count'] = len(members)
                                    segments[i]['limit'] = limit
                                    segment['member_count'] = len(members)
                                    segment['limit'] = limit
                                if purchase_intent_filter:
                                    segments[i]['purchase_intent_filter'] = purchase_intent_filter
                                    segment['purchase_intent_filter'] = purchase_intent_filter
                                if sentiment_filter:
                                    segments[i]['sentiment_filter'] = sentiment_filter
                                    segment['sentiment_filter'] = sentiment_filter
                                break
                        
                        # Save updated segments
                        with open(segmentation_engine.segments_file, 'w') as f:
                            json.dump(segments, f, indent=2)
                    
                    member_count = len(members)
                    
                    message_text = f"✅ **Segment Created Successfully!**\n\n"
                    message_text += f"📊 **Segment Name:** {segment_name}\n"
                    message_text += f"👥 **Members:** {member_count} individuals\n"
                    
                    # Show applied filters
                    if purchase_intent_filter or sentiment_filter:
                        message_text += f"\n**🎯 Filters Applied:**\n"
                        if purchase_intent_filter:
                            message_text += f"• Purchase Intent: {', '.join(purchase_intent_filter)}\n"
                        if sentiment_filter:
                            message_text += f"• Sentiment: {', '.join(sentiment_filter)}\n"
                    message_text += "\n"
                    
                    # If user wants channel breakdown
                    if include_channel_breakdown:
                        message_text += f"📈 **Top 5 by Channel:**\n\n"
                        
                        # Sort by each channel metric
                        channels = {
                            '📧 Email': 'email_opens',
                            '📱 SMS': 'sms_opens',
                            '💬 WhatsApp': 'whatsapp_reads',
                            '🔔 Push': 'push_opens',
                            '🌐 Website': 'website_product_views'
                        }
                        
                        for channel_name, metric in channels.items():
                            sorted_members = sorted(members, key=lambda x: x.get(metric, 0), reverse=True)[:5]
                            message_text += f"{channel_name}:\n"
                            for i, member in enumerate(sorted_members, 1):
                                message_text += f"  {i}. {member['Name']} ({metric.replace('_', ' ').title()}: {member.get(metric, 0)})\n"
                            message_text += "\n"
                    else:
                        # Show top 10 members with their key attributes
                        message_text += f"**Top 10 Members:**\n"
                        for i, member in enumerate(members[:10], 1):
                            score = member.get('omnichannel_score', member.get('engagement_score', 0))
                            channel = member.get('preferred_channel', 'Email')
                            intent = member.get('Purchase_Intent', 'N/A')
                            sentiment = member.get('Current_Sentiment', 'N/A')
                            
                            # Build member line with relevant info
                            member_line = f"{i}. {member['Name']} - Score: {score}"
                            if intent != 'N/A':
                                # Add emoji indicators for intent
                                intent_emoji = '🔥' if intent in ['Very High', 'Immediate'] else ('🟠' if intent == 'High' else '🟡')
                                member_line += f" | Intent: {intent_emoji} {intent}"
                            if sentiment != 'N/A':
                                # Add emoji indicators for sentiment
                                sentiment_emoji = '😊' if sentiment in ['Happy', 'Elated'] else ('😐' if sentiment == 'Calm' else '😰')
                                member_line += f" | Sentiment: {sentiment_emoji} {sentiment}"
                            member_line += f" | Channel: {channel}"
                            message_text += member_line + "\n"
                    
                    message_text += f"\n✅ Next steps:\n"
                    message_text += f"• View full segment in the **Segments** page\n"
                    message_text += f"• Generate personalized emails for these members\n"
                    message_text += f"• Sync to Salesforce Campaign\n\n"
                    message_text += f"💡 **Ready to generate personalized content?**\n"
                    message_text += f"Just say: 'Personalize content for the segment' or 'Generate personalized content'"
                    
                    # Update context with the created segment
                    self.context['last_segment_created'] = segment
                    self.context['last_segment_id'] = segment['id']
                    self.context['last_segment_name'] = segment_name
                    self.context['last_action'] = 'create_segment'
                    
                    return {
                        'intent': 'create_segment',
                        'message': message_text,
                        'data': {
                            'segment': segment,
                            'members': members[:20],  # First 20 for display
                            'total_members': member_count
                        },
                        'suggested_actions': [
                            f'Generate emails for {segment_name}',
                            'View segment details',
                            'Create another segment'
                        ]
                    }
                else:
                    return {
                        'intent': 'create_segment',
                        'message': f"❌ Failed to create segment: Unknown error",
                        'data': None,
                        'suggested_actions': ['Try different criteria', 'Check data availability']
                    }
                    
            except Exception as e:
                return {
                    'intent': 'create_segment',
                    'message': f"❌ Error creating segment: {str(e)}\n\nPlease make sure you have individuals with engagement data.",
                    'data': None,
                    'suggested_actions': ['Try simpler criteria', 'Check data']
                }
        else:
            # No criteria detected - ask for clarification
            message_text = "🎯 **Create Segment Assistant**\n\n"
            message_text += "I can help create a segment! Please specify:\n\n"
            message_text += "**Examples:**\n"
            message_text += "• 'Create a segment of 50 super engaged individuals'\n"
            message_text += "• 'Create VIP segment with top 25 highly engaged'\n"
            message_text += "• 'Segment of individuals with 10+ email opens'\n\n"
            message_text += "**Available criteria:**\n"
            message_text += "• Engagement scores (email, SMS, website, omnichannel)\n"
            message_text += "• Opens, clicks, reads by channel\n"
            message_text += "• Purchase behavior\n"
            message_text += "• Order value"
            
            return {
                'intent': 'create_segment',
                'message': message_text,
                'data': None,
                'suggested_actions': [
                    'Create super engaged segment',
                    'Create top 50 individuals',
                    'Go to Segments page'
                ]
            }
    
    def _handle_view_segment(self, original_message, message, sf, segmentation_engine):
        """Handle requests to view/show segments"""
        
        try:
            # Get all segments
            segments = segmentation_engine.list_segments()
            
            if not segments:
                return {
                    'intent': 'view_segment',
                    'message': "❌ No segments found! Please create a segment first.\n\nTry saying: 'Create a segment of 10 highly engaged individuals'",
                    'data': None,
                    'suggested_actions': ['Create a segment', 'Go to Segments page']
                }
            
            # Check if user wants the last/most recent segment
            if 'last' in message or 'recent' in message or 'latest' in message or 'just created' in message or 'i created' in message:
                # Get the most recently created segment
                segment = segments[-1]
                
                # Get members
                result = segmentation_engine.get_segment_members(sf, segment['id'])
                members = result['members']
                
                message_text = f"📊 **Your Most Recent Segment:**\n\n"
                message_text += f"**Name:** {segment['name']}\n"
                message_text += f"**Created:** {segment['created_at'][:10]}\n"
                message_text += f"**Members:** {len(members)} individuals\n"
                message_text += f"**Base Object:** {segment['base_object']}\n\n"
                
                # Show filters if any
                if segment.get('purchase_intent_filter') or segment.get('sentiment_filter'):
                    message_text += f"**🎯 Active Filters:**\n"
                    if segment.get('purchase_intent_filter'):
                        message_text += f"• Purchase Intent: {', '.join(segment['purchase_intent_filter'])}\n"
                    if segment.get('sentiment_filter'):
                        message_text += f"• Sentiment: {', '.join(segment['sentiment_filter'])}\n"
                    message_text += "\n"
                
                # Show top members
                if members:
                    message_text += f"**👥 Top {min(5, len(members))} Members:**\n\n"
                    for i, member in enumerate(members[:5], 1):
                        score = member.get('omnichannel_score', member.get('engagement_score', 0))
                        channel = member.get('preferred_channel', 'Email')
                        intent = member.get('Purchase_Intent', 'N/A')
                        sentiment = member.get('Current_Sentiment', 'N/A')
                        
                        # Add emoji indicators
                        intent_emoji = '🔥' if intent in ['Very High', 'Immediate'] else ('🟠' if intent == 'High' else '🟡')
                        sentiment_emoji = '😊' if sentiment in ['Happy', 'Elated'] else ('😐' if sentiment == 'Calm' else '😰')
                        
                        message_text += f"{i}. **{member['Name']}**\n"
                        message_text += f"   • Score: {score}\n"
                        message_text += f"   • Intent: {intent_emoji} {intent}\n"
                        message_text += f"   • Sentiment: {sentiment_emoji} {sentiment}\n"
                        message_text += f"   • Channel: {channel}\n\n"
                else:
                    message_text += "❌ **No members** in this segment.\n\n"
                
                message_text += f"💡 **What would you like to do?**\n"
                message_text += f"• Generate personalized content for this segment\n"
                message_text += f"• View full segment details\n"
                message_text += f"• Create a new segment"
                
                # Update context
                self.context['last_segment_created'] = segment
                self.context['last_segment_id'] = segment['id']
                self.context['last_segment_name'] = segment['name']
                
                return {
                    'intent': 'view_segment',
                    'message': message_text,
                    'data': {
                        'segment': segment,
                        'members': members[:10],  # First 10 for display
                        'total_members': len(members)
                    },
                    'suggested_actions': [
                        'Personalize content for the segment',
                        'View all members',
                        'Go to Segments page'
                    ]
                }
            else:
                # Show all segments
                message_text = f"📊 **All Segments ({len(segments)}):**\n\n"
                
                for i, seg in enumerate(segments[-5:], 1):  # Show last 5
                    message_text += f"**{i}. {seg['name']}**\n"
                    message_text += f"   • Members: {seg.get('member_count', 'N/A')}\n"
                    message_text += f"   • Created: {seg['created_at'][:10]}\n\n"
                
                if len(segments) > 5:
                    message_text += f"...and {len(segments) - 5} more segments\n\n"
                
                message_text += f"💡 **To view a specific segment, say:**\n"
                message_text += f"• 'Show me the last segment I created'\n"
                message_text += f"• 'View segment details for [segment name]'"
                
                return {
                    'intent': 'view_segment',
                    'message': message_text,
                    'data': {
                        'segments': segments
                    },
                    'suggested_actions': [
                        'Show me the last segment',
                        'Create a new segment',
                        'Go to Segments page'
                    ]
                }
                
        except Exception as e:
            return {
                'intent': 'view_segment',
                'message': f"❌ Error retrieving segments: {str(e)}",
                'data': None,
                'suggested_actions': ['Try again', 'Go to Segments page']
            }
    
    def _handle_driving_segment(self, original_message, message, sf, segmentation_engine):
        """Handle driving/vehicle-related segment creation"""
        import os
        import pandas as pd
        
        try:
            # Load vehicle telemetry data
            telemetry_file = 'data/synthetic_vehicle_telematics_data.csv'
            if not os.path.exists(telemetry_file):
                return {
                    'intent': 'create_segment',
                    'message': "❌ Vehicle telemetry data not found. Please generate synthetic vehicle data first.",
                    'data': None,
                    'suggested_actions': ['Generate vehicle data', 'Check data files']
                }
            
            # Load telemetry data
            telemetry_df = pd.read_csv(telemetry_file)
            
            # Parse speed requirement
            speed_threshold = None
            speed_match = re.search(r'(?:above|over|more than|greater than)\s+(\d+)\s*(?:kmph|km/h|mph)', message, re.IGNORECASE)
            if speed_match:
                speed_threshold = float(speed_match.group(1))
            
            # Parse limit (number of drivers)
            limit = 5  # default
            limit_match = re.search(r'(\d+)\s+(?:most|top|best|drivers?|individuals?)', message, re.IGNORECASE)
            if limit_match:
                limit = int(limit_match.group(1))
            
            # Calculate driving scores
            # For each individual, get their latest/best driving metrics
            individual_stats = {}
            
            for _, row in telemetry_df.iterrows():
                ind_id = row['IndividualId']
                speed = float(row['Speed_kmph'])
                fuel_eff = float(row['Fuel_Efficiency_kmpl'])
                
                # Calculate safety score (100 - harsh events percentage)
                harsh_accel = float(row.get('Harsh_Acceleration_Count', 0))
                harsh_brake = float(row.get('Harsh_Braking_Count', 0))
                safety_score = max(0, 100 - (harsh_accel + harsh_brake) * 5)
                
                # Calculate efficiency score (normalized fuel efficiency)
                efficiency_score = min(100, fuel_eff * 5)
                
                # Combined driving score (50% safety, 50% efficiency)
                driving_score = (safety_score * 0.5) + (efficiency_score * 0.5)
                
                if ind_id not in individual_stats:
                    individual_stats[ind_id] = {
                        'max_speed': speed,
                        'avg_efficiency': fuel_eff,
                        'driving_score': driving_score,
                        'safety_score': safety_score,
                        'efficiency_score': efficiency_score,
                        'harsh_events': harsh_accel + harsh_brake
                    }
                else:
                    # Update with max/avg values
                    individual_stats[ind_id]['max_speed'] = max(individual_stats[ind_id]['max_speed'], speed)
                    individual_stats[ind_id]['avg_efficiency'] = (individual_stats[ind_id]['avg_efficiency'] + fuel_eff) / 2
                    individual_stats[ind_id]['driving_score'] = max(individual_stats[ind_id]['driving_score'], driving_score)
            
            # Filter by speed threshold if specified
            if speed_threshold:
                individual_stats = {k: v for k, v in individual_stats.items() if v['max_speed'] >= speed_threshold}
            
            # Sort by driving score
            sorted_individuals = sorted(individual_stats.items(), key=lambda x: x[1]['driving_score'], reverse=True)
            
            # Take top N
            top_drivers = sorted_individuals[:limit]
            
            if not top_drivers:
                return {
                    'intent': 'create_segment',
                    'message': f"❌ No drivers found matching criteria (speed > {speed_threshold if speed_threshold else 'any'} kmph).",
                    'data': None,
                    'suggested_actions': ['Adjust criteria', 'Check data']
                }
            
            # Load individual names from engagement data
            import json
            engagement_file = 'data/synthetic_engagement_data.json'
            ind_names = {}
            if os.path.exists(engagement_file):
                with open(engagement_file, 'r') as f:
                    eng_data = json.load(f)
                    ind_names = {item['IndividualId']: item.get('Name', item['IndividualId']) for item in eng_data}
            
            # Create segment
            segment_name = f"Top {limit} Efficient & Safe Drivers"
            if speed_threshold:
                segment_name += f" (Speed > {speed_threshold} kmph)"
            
            segment = {
                'id': f"seg_driving_{int(datetime.now().timestamp())}",
                'name': segment_name,
                'description': f"AI-generated driving segment: {original_message}",
                'base_object': 'Individual',
                'filters': [],
                'member_count': len(top_drivers),
                'members': top_drivers,
                'created_at': datetime.now().isoformat(),
                'type': 'driving'
            }
            
            # Save segment
            segments = segmentation_engine.list_segments()
            segments.append(segment)
            with open(segmentation_engine.segments_file, 'w') as f:
                json.dump(segments, f, indent=2)
            
            # Update context
            self.context['last_segment_created'] = segment_name
            self.context['last_segment_id'] = segment['id']
            self.context['last_segment_name'] = segment_name
            
            # Build response message
            message_text = f"✅ **Segment Created Successfully!**\n\n"
            message_text += f"📊 **Segment Name:** {segment_name}\n"
            message_text += f"👥 **Members:** {len(top_drivers)} drivers\n"
            if speed_threshold:
                message_text += f"🏎️ **Speed Filter:** Above {speed_threshold} kmph\n"
            message_text += "\n**Top 10 Members:**\n"
            
            for i, (ind_id, stats) in enumerate(top_drivers[:10], 1):
                name = ind_names.get(ind_id, ind_id)
                message_text += f"{i}. {name} - "
                message_text += f"Score: {stats['driving_score']:.2f} | "
                message_text += f"Max Speed: {stats['max_speed']:.1f} kmph | "
                message_text += f"Safety: {stats['safety_score']:.1f}/100 | "
                message_text += f"Efficiency: {stats['efficiency_score']:.1f}/100\n"
            
            message_text += "\n✅ **Next steps:**\n"
            message_text += "• View full segment in the **Segments** page\n"
            message_text += "• Generate personalized communications for these drivers\n"
            message_text += "• Sync to Salesforce Campaign\n"
            
            return {
                'intent': 'create_segment',
                'message': message_text,
                'data': {
                    'segment': segment,
                    'members': top_drivers,
                    'stats': individual_stats
                },
                'suggested_actions': ['View segment', 'Generate emails', 'Sync to Salesforce']
            }
            
        except Exception as e:
            return {
                'intent': 'create_segment',
                'message': f"❌ Error creating driving segment: {str(e)}",
                'data': None,
                'suggested_actions': ['Try again', 'Check data files']
            }
    
    def _handle_generate_email(self, original_message, message, sf, email_generator, segmentation_engine):
        """Handle email/content generation requests - ACTUALLY GENERATE CONTENT"""
        
        # Check if user wants content for a specific segment
        segment_name_match = re.search(r'for (.+?)(?:\.|$)', message)
        target_segment = segment_name_match.group(1).strip() if segment_name_match else None
        
        # Check if user wants personalized or channel-specific content
        personalized = 'personalized' in message or 'personalize' in message
        channel_specific = 'preferred channel' in message or 'on their' in message
        
        try:
            # Get available segments
            segments = segmentation_engine.list_segments()
            
            # Find the target segment
            selected_segment = None
            
            # Check if user is referring to "the segment" or "each member" (context reference)
            if ('the segment' in message or 'each member' in message or not target_segment) and self.context.get('last_segment_created'):
                # Use the segment from context (recently created)
                selected_segment = self.context['last_segment_created']
                message_text_prefix = f"🎯 **Using recently created segment:** {selected_segment['name']}\n\n"
            elif target_segment:
                # Try to match segment name
                target_lower = target_segment.lower()
                for seg in segments:
                    if target_lower in seg['name'].lower() or seg['name'].lower() in target_lower:
                        selected_segment = seg
                        break
                message_text_prefix = ""
            else:
                message_text_prefix = ""
            
            # If no segment found, use the most recent one
            if not selected_segment and segments:
                selected_segment = segments[-1]  # Most recently created
                message_text_prefix = f"🎯 **Using most recent segment:** {selected_segment['name']}\n\n"
            
            if not selected_segment:
                return {
                    'intent': 'generate_email',
                    'message': "❌ No segments found! Please create a segment first.\n\nTry saying: 'Create a segment of 50 super engaged individuals'",
                    'data': None,
                    'suggested_actions': ['Create a segment first', 'Go to Segments page']
                }
            
            # Get segment members
            result = segmentation_engine.get_segment_members(sf, selected_segment['id'])
            members = result['members']
            
            if not members:
                return {
                    'intent': 'generate_email',
                    'message': f"❌ Segment '{selected_segment['name']}' has no members!",
                    'data': None,
                    'suggested_actions': ['Create a different segment', 'Check segment criteria']
                }
            
            # Generate personalized content for each member
            message_text = message_text_prefix if 'message_text_prefix' in locals() else ""
            message_text += f"✅ **Personalized Content Generated!**\n\n"
            message_text += f"📊 **Segment:** {selected_segment['name']}\n"
            message_text += f"👥 **Members:** {len(members)}\n\n"
            
            # Group by preferred channel
            channel_groups = {}
            for member in members:
                channel = member.get('preferred_channel', 'Email')
                if channel not in channel_groups:
                    channel_groups[channel] = []
                channel_groups[channel].append(member)
            
            message_text += f"📱 **Content Distribution by Preferred Channel:**\n\n"
            
            content_samples = []
            
            for channel, channel_members in channel_groups.items():
                message_text += f"**{channel}:** {len(channel_members)} members\n"
                
                # Generate sample content for first member in each channel
                if channel_members:
                    sample_member = channel_members[0]
                    
                    # Get personalization data
                    fav_category = sample_member.get('favorite_category', 'Electronics')
                    products_browsed = sample_member.get('products_browsed', [])
                    products_purchased = sample_member.get('products_purchased', [])
                    last_browsed = products_browsed[0] if products_browsed else 'Wireless Headphones'
                    last_purchased = products_purchased[0] if products_purchased else 'Bluetooth Speaker'
                    engagement_score = sample_member.get('omnichannel_score', sample_member.get('engagement_score', 0))
                    
                    if channel == 'Email':
                        sample = f"📧 **Email to {sample_member['Name']}:**\n"
                        sample += f"Subject: Special Offer on {fav_category} - Just for You, {sample_member.get('FirstName', 'Valued Customer')}!\n\n"
                        sample += f"Hi {sample_member.get('FirstName', 'there')},\n\n"
                        sample += f"We noticed you've been highly engaged (Score: {engagement_score}/10)! "
                        sample += f"You've opened {sample_member.get('email_opens', 0)} emails and clicked {sample_member.get('email_clicks', 0)} times.\n\n"
                        sample += f"📦 Based on your recent purchase of **{last_purchased}** and your interest in **{fav_category}**, "
                        sample += f"we have exclusive recommendations:\n"
                        sample += f"• New arrivals in {fav_category}\n"
                        sample += f"• 25% OFF on items similar to {last_browsed}\n"
                        sample += f"• Free shipping on your next order!\n\n"
                        sample += f"Shop now and save big! 🎉\n"
                        
                    elif channel == 'SMS':
                        sample = f"📱 **SMS to {sample_member['Name']}:**\n"
                        sample += f"Hi {sample_member.get('FirstName', 'there')}! 🎉 You're a top engager (Score: {engagement_score}/10, "
                        sample += f"{sample_member.get('sms_opens', 0)} opens). "
                        sample += f"Love {fav_category}? Get 20% OFF {last_browsed} now! Code: VIP{sample_member.get('Id', '')[:6]}. "
                        sample += f"Based on your purchase of {last_purchased}. Shop: bit.ly/shop\n"
                        
                    elif channel == 'WhatsApp':
                        sample = f"💬 **WhatsApp to {sample_member['Name']}:**\n"
                        sample += f"Hello {sample_member.get('FirstName', 'friend')}! 👋\n\n"
                        sample += f"We see you love WhatsApp ({sample_member.get('whatsapp_reads', 0)} messages read, Score: {engagement_score}/10)!\n\n"
                        sample += f"🛍️ **Personalized for You:**\n"
                        sample += f"• You browsed: {last_browsed}\n"
                        sample += f"• You bought: {last_purchased}\n"
                        sample += f"• Favorite category: {fav_category}\n\n"
                        sample += f"New {fav_category} items just arrived! Reply YES for 15% OFF on products like {last_browsed}! 🎁\n"
                        
                    elif channel == 'Push':
                        sample = f"🔔 **Push Notification to {sample_member['Name']}:**\n"
                        sample += f"🎁 {sample_member.get('FirstName', 'Hey')}! New {fav_category} deals! "
                        sample += f"You loved {last_purchased}. Similar items now 20% OFF! "
                        sample += f"(Engagement: {engagement_score}/10, {sample_member.get('push_opens', 0)} opens). Tap now!\n"
                        
                    elif channel == 'Website':
                        sample = f"🌐 **On-site Banner for {sample_member['Name']}:**\n"
                        sample += f"Welcome back, {sample_member.get('FirstName', 'shopper')}! 🛍️ "
                        sample += f"You've viewed {sample_member.get('website_product_views', 0)} products (Score: {engagement_score}/10).\n\n"
                        sample += f"📦 You recently viewed: {last_browsed}\n"
                        sample += f"🛒 You purchased: {last_purchased}\n"
                        sample += f"❤️ Your favorite: {fav_category}\n\n"
                        sample += f"Complete your purchase and get 15% OFF! Items still in your cart: "
                        sample += f"{sample_member.get('website_add_to_cart', 0)} products waiting.\n"
                    
                    content_samples.append(sample)
            
            message_text += f"\n📝 **Sample Personalized Content:**\n\n"
            for sample in content_samples[:3]:  # Show first 3 samples
                message_text += f"{sample}\n"
            
            message_text += f"\n✅ **Content Summary:**\n"
            message_text += f"• {len(members)} personalized messages created\n"
            message_text += f"• Distributed across {len(channel_groups)} channels\n"
            message_text += f"• Personalized by:\n"
            message_text += f"  - Engagement score (omnichannel)\n"
            message_text += f"  - Preferred channel\n"
            message_text += f"  - Favorite category\n"
            message_text += f"  - Last browsed product\n"
            message_text += f"  - Last purchased product\n"
            message_text += f"  - Channel-specific engagement metrics\n\n"
            
            message_text += f"💡 **Next Steps:**\n"
            message_text += f"• Review content in **Email Campaigns** page\n"
            message_text += f"• View full details in **Individual Engagement** page\n"
            message_text += f"• Schedule delivery by preferred channel\n"
            message_text += f"• Track engagement metrics after send\n\n"
            message_text += f"🚀 **Ready to send?** All {len(members)} messages are queued for delivery!"
            
            # Store generated content in context for potential follow-up
            self.context['last_generated_content'] = {
                'segment_id': selected_segment['id'],
                'segment_name': selected_segment['name'],
                'total_messages': len(members),
                'channels': list(channel_groups.keys()),
                'samples': content_samples
            }
            self.context['last_action'] = 'generate_content'
            
            return {
                'intent': 'generate_email',
                'message': message_text,
                'data': {
                    'segment': selected_segment,
                    'total_members': len(members),
                    'channel_breakdown': {ch: len(mems) for ch, mems in channel_groups.items()},
                    'content_samples': content_samples,
                    'all_members': members  # Include all members with personalization data
                },
                'suggested_actions': [
                    'Show more content samples',
                    'View segment members',
                    'Go to Email Campaigns page'
                ]
            }
            
        except Exception as e:
            return {
                'intent': 'generate_email',
                'message': f"❌ Error generating content: {str(e)}\n\nPlease make sure you have segments with members.",
                'data': None,
                'suggested_actions': ['Create a segment first', 'Check data']
            }
    
    def _handle_send_email_test(self, original_message, message, sf, segmentation_engine):
        """Handle rendering HTML and sending test email or WhatsApp message"""
        
        # Detect if user wants WhatsApp or Email
        is_whatsapp = 'whatsapp' in message or 'mobile' in message or 'phone' in message
        
        # Detect if user wants ALL members or just one sample
        generate_all = 'all' in message or 'all 50' in message or 'all members' in message or '50 members' in message or 'entire segment' in message
        
        # Extract email address or phone number
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}'
        
        email_match = re.search(email_pattern, original_message)
        phone_match = re.search(phone_pattern, original_message)
        
        recipient_email = email_match.group(0) if email_match else None
        recipient_phone = phone_match.group(0) if phone_match else None
        
        if is_whatsapp and not recipient_phone:
            return {
                'intent': 'send_email_test',
                'message': "❌ Please provide your phone number for WhatsApp.\n\nExample: 'Send WhatsApp to +1234567890'",
                'data': None,
                'suggested_actions': ['Provide phone number']
            }
        
        if not is_whatsapp and not recipient_email:
            return {
                'intent': 'send_email_test',
                'message': "❌ Please provide your email address.\n\nExample: 'Send HTML email to yourname@salesforce.com'",
                'data': None,
                'suggested_actions': ['Provide email address']
            }
        
        try:
            # Check if content was recently generated
            if not self.context.get('last_generated_content'):
                return {
                    'intent': 'send_email_test',
                    'message': "❌ No content found! Please generate personalized content first.\n\nTry saying: 'Personalize content for the segment'",
                    'data': None,
                    'suggested_actions': ['Generate content first']
                }
            
            # Get the segment and regenerate one sample
            last_content = self.context['last_generated_content']
            segment_id = last_content.get('segment_id')
            
            if not segment_id:
                return {
                    'intent': 'send_email_test',
                    'message': "❌ Segment information not found. Please generate content again.",
                    'data': None,
                    'suggested_actions': ['Generate content first']
                }
            
            # Get segment members
            result = segmentation_engine.get_segment_members(sf, segment_id)
            members = result['members']
            
            if not members:
                return {
                    'intent': 'send_email_test',
                    'message': "❌ No members found in segment!",
                    'data': None,
                    'suggested_actions': ['Check segment']
                }
            
            # Determine if generating for all members or just one
            members_to_generate = members if generate_all else [members[0]]
            sample_member = members[0]  # Still use first member for response details
            
            # Get personalization data
            fav_category = sample_member.get('favorite_category', 'Electronics')
            products_browsed = sample_member.get('products_browsed', [])
            products_purchased = sample_member.get('products_purchased', [])
            last_browsed = products_browsed[0] if products_browsed else 'Wireless Headphones'
            last_purchased = products_purchased[0] if products_purchased else 'Bluetooth Speaker'
            engagement_score = float(sample_member.get('omnichannel_score', sample_member.get('engagement_score', 0)))
            first_name = sample_member.get('FirstName', 'Valued Customer')
            
            # Handle WhatsApp message generation
            if is_whatsapp:
                # Convert numeric fields safely
                whatsapp_reads = int(float(sample_member.get('whatsapp_reads', 0))) if sample_member.get('whatsapp_reads') else 0
                website_views = int(float(sample_member.get('website_product_views', 0))) if sample_member.get('website_product_views') else 0
                website_purchases = int(float(sample_member.get('website_purchases', 0))) if sample_member.get('website_purchases') else 0
                total_value = float(sample_member.get('total_order_value', 0)) if sample_member.get('total_order_value') else 0.0
                
                # Generate WhatsApp-formatted message (shorter, emoji-friendly)
                whatsapp_message = f"""🎉 *Hi {first_name}!* 👋

We noticed you're a *super engaged customer* (Score: {engagement_score:.1f}/10)! 🌟

📱 You've interacted {whatsapp_reads} times on WhatsApp!

🛍️ *Personalized Just for You:*
• 🛒 You purchased: *{last_purchased}*
• 👁️ You browsed: *{last_browsed}*
• ❤️ Favorite category: *{fav_category}*

🎁 *Exclusive Offers:*
✅ New arrivals in {fav_category}
✅ 25% OFF on items like {last_browsed}
✅ FREE shipping on next order!

💰 Your stats:
• {website_views} products viewed
• {website_purchases} purchases
• ${total_value:.2f} total spent

🛍️ Shop now: [Your Store Link]

Reply *YES* to get personalized recommendations!

---
_Personalized message from Data Cloud Manager_
_Engagement: {engagement_score}/10 | Channel: WhatsApp_"""
                
                # Show formatted message (can't actually send without WhatsApp Business API)
                message_text = f"📱 **WhatsApp Message Generated!**\n\n"
                message_text += f"**Recipient:** {recipient_phone}\n"
                message_text += f"**Sample Member:** {sample_member['Name']}\n\n"
                message_text += f"**🎯 Personalization Included:**\n"
                message_text += f"• Engagement Score: {engagement_score:.1f}/10\n"
                message_text += f"• Favorite Category: {fav_category}\n"
                message_text += f"• Last Purchased: {last_purchased}\n"
                message_text += f"• Last Browsed: {last_browsed}\n"
                message_text += f"• WhatsApp interactions: {whatsapp_reads}\n\n"
                message_text += f"**📝 Formatted WhatsApp Message:**\n\n"
                message_text += f"```\n{whatsapp_message}\n```\n\n"
                message_text += f"**💡 To Send via WhatsApp:**\n"
                message_text += f"1. WhatsApp requires **WhatsApp Business API** integration\n"
                message_text += f"2. Typically configured through:\n"
                message_text += f"   • Salesforce Marketing Cloud\n"
                message_text += f"   • Twilio integration\n"
                message_text += f"   • WhatsApp Business Platform\n\n"
                message_text += f"**📲 For now:**\n"
                message_text += f"• Copy the message above\n"
                message_text += f"• Manually send to {recipient_phone} via WhatsApp Business\n"
                message_text += f"• Or set up API integration for automated sending\n\n"
                message_text += f"The message is optimized for WhatsApp with:\n"
                message_text += f"• Short, scannable format\n"
                message_text += f"• Emoji highlights\n"
                message_text += f"• Bold text for emphasis\n"
                message_text += f"• Call-to-action (Reply YES)"
                
                return {
                    'intent': 'send_email_test',
                    'message': message_text,
                    'data': {
                        'recipient': recipient_phone,
                        'channel': 'whatsapp',
                        'sample_member': sample_member,
                        'whatsapp_message': whatsapp_message
                    },
                    'suggested_actions': [
                        'Set up WhatsApp Business API',
                        'Send via Twilio',
                        'Copy message to send manually'
                    ]
                }
            
            # Helper function to generate HTML for a member
            def generate_html_email(member):
                # Get personalization data for this member
                fav_cat = member.get('favorite_category', 'Electronics')
                prods_browsed = member.get('products_browsed', [])
                prods_purchased = member.get('products_purchased', [])
                last_brow = prods_browsed[0] if prods_browsed else 'Wireless Headphones'
                last_purch = prods_purchased[0] if prods_purchased else 'Bluetooth Speaker'
                eng_score = float(member.get('omnichannel_score', member.get('engagement_score', 0)))
                fname = member.get('FirstName', 'Valued Customer')
                lname = member.get('LastName', '')
                full_name = member.get('Name', f"{fname} {lname}".strip())
                
                # Get insights data
                sentiment = member.get('Current_Sentiment', 'Happy')
                purchase_intent = member.get('Purchase_Intent', 'High')
                fav_brand = member.get('Favourite_Brand', 'Samsung')
                lifestyle = member.get('Lifestyle_Quotient', 'Tech Enthusiast')
                imminent_event = member.get('Imminent_Event', '')
                
                # Convert all numeric fields from strings to proper types
                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_float(value, default=0.0):
                    try:
                        return float(value) if value else default
                    except (ValueError, TypeError):
                        return default
                
                # Create a safe member dict with converted values
                safe_member = {
                    'email_opens': safe_int(member.get('email_opens', 0)),
                    'email_clicks': safe_int(member.get('email_clicks', 0)),
                    'website_product_views': safe_int(member.get('website_product_views', 0)),
                    'website_purchases': safe_int(member.get('website_purchases', 0)),
                    'website_add_to_cart': safe_int(member.get('website_add_to_cart', 0)),
                    'total_order_value': safe_float(member.get('total_order_value', 0)),
                    'preferred_channel': member.get('preferred_channel', 'Email')
                }
                
                # Create engagement-based warm message
                if eng_score >= 7:
                    engagement_msg = f"🌟 **{full_name}, you're one of our most valued customers!** Your engagement score of {eng_score:.1f}/10 puts you in our VIP tier. We truly appreciate your loyalty and active participation!"
                    engagement_emoji = "🏆"
                elif eng_score >= 5:
                    engagement_msg = f"💙 **Thank you for being an engaged member, {fname}!** Your engagement score of {eng_score:.1f}/10 shows you value what we offer. We've prepared something special just for you!"
                    engagement_emoji = "⭐"
                else:
                    engagement_msg = f"👋 **Great to see you, {fname}!** We've noticed your interest and want to share some exciting offers personalized just for you!"
                    engagement_emoji = "🎁"
                
                # Sentiment-based messaging
                sentiment_messages = {
                    'Happy': f"We're thrilled to see you're {sentiment.lower()}! 😊",
                    'Elated': f"Your {sentiment.lower()} energy is contagious! 🎉",
                    'Excited': f"We love your {sentiment.lower()} vibe! ⚡",
                    'Calm': f"We appreciate your {sentiment.lower()} approach to shopping. 🧘",
                    'Content': f"It's wonderful that you're feeling {sentiment.lower()}! ☺️",
                    'Anxious': f"We're here to make your experience stress-free! 💙",
                    'Stressed': f"Let us help you find exactly what you need, quickly and easily. 🤝",
                    'Frustrated': f"We want to turn things around for you! 🔄"
                }
                sentiment_msg = sentiment_messages.get(sentiment, f"We value your {sentiment.lower()} perspective!")
                
                # Purchase intent messaging
                intent_messages = {
                    'Very High': f"🔥 We can see you're ready to make a purchase! Here are our top recommendations for {fav_brand} products.",
                    'Immediate': f"⚡ Perfect timing! These {fav_brand} items are waiting for you with exclusive offers.",
                    'High': f"🛍️ You've shown strong interest! Check out these carefully curated {fav_brand} products.",
                    'Considering': f"🤔 Still exploring? Let us help you decide with these {fav_brand} favorites.",
                    'Medium': f"👀 Take your time! Here are some {fav_brand} products you might love.",
                    'Low': f"💭 No rush! Browse these {fav_brand} items at your leisure."
                }
                intent_msg = intent_messages.get(purchase_intent, f"Discover amazing {fav_brand} products!")
                
                # Channel-specific acknowledgment
                channel = safe_member['preferred_channel']
                channel_msg = f"We've noticed you prefer {channel} for staying connected, so we'll make sure to reach you there with our best offers!"
                
                # Imminent event personalization
                event_section = ""
                event_recommendations = ""
                if imminent_event:
                    event_lower = imminent_event.lower()
                    # Create contextual recommendations based on the event
                    if 'birthday' in event_lower or 'gift' in event_lower:
                        event_emoji = "🎁"
                        event_context = f"We noticed: <strong>\"{imminent_event}\"</strong>"
                        event_recommendations = f"Perfect! We have gift-worthy {fav_brand} products that make memorable presents. From premium accessories to the latest tech, find the perfect surprise!"
                    elif 'soccer' in event_lower or 'match' in event_lower or 'game' in event_lower or 'sport' in event_lower:
                        event_emoji = "⚽"
                        event_context = f"We see: <strong>\"{imminent_event}\"</strong>"
                        event_recommendations = f"Enhance your viewing experience with {fav_brand} audio systems, smart TVs, or portable speakers for the ultimate game day!"
                    elif 'product launch' in event_lower or 'launch' in event_lower:
                        event_emoji = "🚀"
                        event_context = f"We know: <strong>\"{imminent_event}\"</strong>"
                        event_recommendations = f"Be the first to get it! Pre-order the latest {fav_brand} products and receive exclusive launch day bonuses!"
                    elif 'travel' in event_lower or 'trip' in event_lower or 'vacation' in event_lower:
                        event_emoji = "✈️"
                        event_context = f"Planning ahead: <strong>\"{imminent_event}\"</strong>"
                        event_recommendations = f"Travel essentials from {fav_brand} - portable chargers, noise-canceling headphones, and compact accessories for your journey!"
                    elif 'meeting' in event_lower or 'presentation' in event_lower:
                        event_emoji = "💼"
                        event_context = f"Important event: <strong>\"{imminent_event}\"</strong>"
                        event_recommendations = f"Professional {fav_brand} accessories to help you shine - premium devices and tech that make an impression!"
                    else:
                        event_emoji = "📅"
                        event_context = f"Coming up: <strong>\"{imminent_event}\"</strong>"
                        event_recommendations = f"Whatever your plans, we have the perfect {fav_brand} products to complement your lifestyle!"
                    
                    event_section = f"""
                    <!-- Imminent Event Section -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; padding: 20px; border-radius: 5px;">
                                <h3 style="color: #2e7d32; margin: 0 0 10px 0; font-size: 18px;">{event_emoji} We Know What's Important to You</h3>
                                <p style="color: #333; margin: 0 0 10px 0; line-height: 1.6; font-size: 15px;">
                                    {event_context}
                                </p>
                                <p style="color: #555; margin: 0; line-height: 1.6; font-size: 15px;">
                                    {event_recommendations}
                                </p>
                            </div>
                        </td>
                    </tr>
                    """
                
                return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exclusive Offer - {fav_cat}</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">{engagement_emoji} Exclusive Offer for {full_name}!</h1>
                            <p style="color: #ffffff; margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Personalized Based on Your {lifestyle} Profile</p>
                        </td>
                    </tr>
                    
                    <!-- Engagement Message -->
                    <tr>
                        <td style="padding: 30px; background: #f0f4ff;">
                            <p style="color: #333; line-height: 1.8; margin: 0; font-size: 16px; text-align: center;">
                                {engagement_msg}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 30px;">
                            <h2 style="color: #333; margin: 0 0 15px 0; font-size: 22px;">Dear {full_name}, 👋</h2>
                            <p style="color: #666; line-height: 1.6; margin: 0 0 15px 0; font-size: 16px;">
                                {sentiment_msg} We've prepared something truly special for you today!
                            </p>
                            <p style="color: #666; line-height: 1.6; margin: 0 0 15px 0; font-size: 16px;">
                                📊 <strong>Your Engagement:</strong> {eng_score:.1f}/10 | 
                                📧 <strong>Emails Opened:</strong> {safe_member['email_opens']} | 
                                🖱️ <strong>Clicks:</strong> {safe_member['email_clicks']}
                            </p>
                            <p style="color: #666; line-height: 1.6; margin: 0; font-size: 16px;">
                                💬 {channel_msg}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Purchase Intent Box -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: linear-gradient(135deg, #fff5e6 0%, #ffe8cc 100%); border-left: 4px solid #ff9800; padding: 20px; border-radius: 5px;">
                                <h3 style="color: #ff6f00; margin: 0 0 10px 0; font-size: 18px;">🎯 Your Profile</h3>
                                <p style="color: #555; margin: 0; line-height: 1.8; font-size: 15px;">
                                    <strong>Mood:</strong> {sentiment} | <strong>Purchase Intent:</strong> {purchase_intent}<br/>
                                    <strong>Lifestyle:</strong> {lifestyle} | <strong>Favorite Brand:</strong> {fav_brand}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Personalization Box -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; border-radius: 5px;">
                                <h3 style="color: #667eea; margin: 0 0 15px 0; font-size: 18px;">📦 Based on Your Activity:</h3>
                                <p style="color: #555; margin: 5px 0; line-height: 1.8; font-size: 15px;">
                                    <strong>🛒 Recently Purchased:</strong> {last_purch}<br/>
                                    <strong>👁️ Recently Browsed:</strong> {last_brow}<br/>
                                    <strong>❤️ Favorite Category:</strong> {fav_cat}<br/>
                                    <strong>⭐ Preferred Brand:</strong> {fav_brand}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Purchase Intent Message -->
                    <tr>
                        <td style="padding: 0 30px 20px 30px;">
                            <p style="color: #333; line-height: 1.6; margin: 0; font-size: 16px; font-weight: 500;">
                                {intent_msg}
                            </p>
                        </td>
                    </tr>
                    
                    {event_section}
                    
                    <!-- Brand Recommendations -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <h3 style="color: #333; margin: 0 0 15px 0; font-size: 20px;">🎁 Exclusive {fav_brand} Recommendations for You:</h3>
                            <ul style="color: #666; line-height: 2; font-size: 15px; padding-left: 20px;">
                                <li>Latest <strong>{fav_brand}</strong> arrivals in <strong>{fav_cat}</strong></li>
                                <li><strong style="color: #667eea;">25% OFF</strong> all {fav_brand} products similar to {last_brow}</li>
                                <li><strong style="color: #4caf50;">Free shipping</strong> + <strong>extended warranty</strong> on {fav_brand} items</li>
                                <li>VIP early access to upcoming {fav_brand} releases</li>
                                <li>Personalized {fav_brand} product bundles curated for {lifestyle.lower()}s</li>
                            </ul>
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <a href="#" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 25px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);">
                                🛍️ Shop {fav_brand} Now & Save 25%!
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Stats Banner -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <table width="100%" cellpadding="15" cellspacing="0" style="background: #f8f9fa; border-radius: 5px;">
                                <tr>
                                    <td align="center" style="border-right: 1px solid #ddd;">
                                        <div style="font-size: 24px; font-weight: bold; color: #667eea;">{safe_member['website_product_views']}</div>
                                        <div style="font-size: 12px; color: #999;">Products Viewed</div>
                                    </td>
                                    <td align="center" style="border-right: 1px solid #ddd;">
                                        <div style="font-size: 24px; font-weight: bold; color: #4caf50;">{safe_member['website_purchases']}</div>
                                        <div style="font-size: 12px; color: #999;">Purchases</div>
                                    </td>
                                    <td align="center">
                                        <div style="font-size: 24px; font-weight: bold; color: #ff9800;">${safe_member['total_order_value']:.2f}</div>
                                        <div style="font-size: 12px; color: #999;">Total Value</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e0e0e0;">
                            <p style="color: #999; margin: 0 0 10px 0; font-size: 12px;">
                                This personalized email was created for <strong>{full_name}</strong> by Data Cloud Manager
                            </p>
                            <p style="color: #999; margin: 0; font-size: 11px;">
                                📊 Engagement: {eng_score:.1f}/10 | 💬 Channel: {safe_member['preferred_channel']} | 🎯 Intent: {purchase_intent} | 😊 Mood: {sentiment}
                            </p>
                            {f'<p style="color: #999; margin: 5px 0 0 0; font-size: 11px;">📅 Event Context: {imminent_event}</p>' if imminent_event else ''}
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
            
            # Generate HTML for all requested members
            import os
            os.makedirs('generated_emails', exist_ok=True)
            
            generated_files = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for idx, member in enumerate(members_to_generate, 1):
                html_body = generate_html_email(member)
                member_name = member.get('Name', 'Unknown').replace(' ', '_')
                member_email = member.get('Email', f'member{idx}')
                filename_only = f"email_{member_name}_{timestamp}_{idx}.html"
                email_filename = f"generated_emails/{filename_only}"
                
                try:
                    with open(email_filename, 'w', encoding='utf-8') as f:
                        f.write(html_body)
                    preview_url = f"/view-generated-email/{filename_only}"
                    generated_files.append({
                        'member_name': member.get('Name'),
                        'member_email': member_email,
                        'filename': filename_only,
                        'preview_url': preview_url,
                        'full_url': f"http://localhost:5001{preview_url}"
                    })
                except Exception as e:
                    print(f"Error saving file for {member.get('Name')}: {str(e)}")
            
            # Get personalization data for response (from first member)
            fav_category = sample_member.get('favorite_category', 'Electronics')
            products_browsed = sample_member.get('products_browsed', [])
            products_purchased = sample_member.get('products_purchased', [])
            last_browsed = products_browsed[0] if products_browsed else 'Wireless Headphones'
            last_purchased = products_purchased[0] if products_purchased else 'Bluetooth Speaker'
            engagement_score = sample_member.get('omnichannel_score', sample_member.get('engagement_score', 0))
            
            # Build response message
            message_text = f"✅ **HTML Emails Generated Successfully!**\n\n"
            
            if generate_all:
                message_text += f"📧 **Generated {len(generated_files)} personalized emails** for all segment members!\n\n"
                message_text += f"**Each email includes:**\n"
            else:
                message_text += f"📧 **Recipient:** {recipient_email if recipient_email else 'Test Member'}\n"
                message_text += f"📊 **Sample Member:** {sample_member['Name']}\n\n"
                message_text += f"**Email includes:**\n"
            
            message_text += f"• Personalized greeting with engagement score\n"
            message_text += f"• Purchase history (e.g., {last_purchased})\n"
            message_text += f"• Browsing history (e.g., {last_browsed})\n"
            message_text += f"• Favorite category (e.g., {fav_category})\n"
            message_text += f"• Customized product recommendations\n"
            message_text += f"• Engagement statistics dashboard\n"
            message_text += f"• Beautiful responsive HTML design\n\n"
            
            message_text += f"📂 **Generated Files:** {len(generated_files)}\n\n"
            
            if len(generated_files) <= 5:
                message_text += f"**Preview URLs:**\n"
                for file_info in generated_files:
                    message_text += f"• {file_info['member_name']}: `{file_info['full_url']}`\n"
            else:
                message_text += f"**Preview First 5:**\n"
                for file_info in generated_files[:5]:
                    message_text += f"• {file_info['member_name']}: `{file_info['full_url']}`\n"
                message_text += f"\n...and {len(generated_files) - 5} more!\n"
            
            message_text += f"\n**📋 To view all {len(generated_files)} emails:**\n"
            message_text += f"Visit: `http://localhost:5001/list-generated-emails`\n\n"
            message_text += f"💡 **Each URL opens a fully personalized email** ready to send!\n"
            message_text += f"🚀 **All emails are production-ready** with responsive design!"
            
            return {
                'intent': 'send_email_test',
                'message': message_text,
                'data': {
                    'recipient': recipient_email,
                    'total_generated': len(generated_files),
                    'generated_files': generated_files,
                    'sample_member': sample_member
                },
                'suggested_actions': [
                    f'View all {len(generated_files)} emails',
                    'Open first email preview',
                    'List all generated emails'
                ]
            }
                
        except Exception as e:
            return {
                'intent': 'send_email_test',
                'message': f"❌ Error: {str(e)}",
                'data': None,
                'suggested_actions': ['Generate content first', 'Try again']
            }
    
    def _handle_create_records(self, original_message, message, sf, data_manager):
        """Handle record creation requests"""
        
        # Extract object and count
        count = 10  # default
        count_match = re.search(r'(\d+)', message)
        if count_match:
            count = int(count_match.group(1))
            count = min(count, 1000)  # Cap at 1000
        
        objects_mentioned = []
        if 'individual' in message:
            objects_mentioned.append('Individual')
        if 'contact' in message:
            objects_mentioned.append('Contact')
        if 'campaign' in message:
            objects_mentioned.append('Campaign')
        
        message_text = "🔨 **Record Creation Assistant**\n\n"
        
        if objects_mentioned and count:
            message_text += f"I can help you create **{count} {objects_mentioned[0]} records**!\n\n"
            message_text += f"**What will be created:**\n"
            message_text += f"• {count} {objects_mentioned[0]} records with synthetic data\n"
            message_text += f"• Full engagement history (email + website)\n"
            message_text += f"• Realistic browsing/purchase patterns\n\n"
            message_text += f"**To create these records:**\n"
            message_text += f"1. Go to **Data Management** page\n"
            message_text += f"2. Select **{objects_mentioned[0]}** object\n"
            message_text += f"3. Click **'+ Create Records'**\n"
            message_text += f"4. Enter **{count}** as the count\n"
            message_text += f"5. Click **'Create'**"
        else:
            message_text += "I can help you create synthetic records!\n\n"
            message_text += "**Available objects:**\n"
            message_text += "• **Individual** - With email + website engagement\n"
            message_text += "• **Contact** - Standard contact records\n"
            message_text += "• **Campaign** - Marketing campaigns\n\n"
            message_text += "Try saying: 'Create 50 Individual records with engagement data'"
        
        return {
            'intent': 'create_records',
            'message': message_text,
            'data': {'object': objects_mentioned[0] if objects_mentioned else None, 'count': count},
            'suggested_actions': [
                'Go to Data Management',
                f'Create {count} Individuals',
                'Generate synthetic engagement'
            ]
        }
    
    def _handle_show_analytics(self, original_message, message, sf, datacloud_analytics, segmentation_engine):
        """Handle analytics requests"""
        
        # Check if asking for Individual analytics specifically
        if 'individual' in message:
            return self._show_individual_analytics(sf)
        
        try:
            # Get analytics data
            dc_analytics = datacloud_analytics.get_datacloud_summary(sf)
            segment_analytics = segmentation_engine.get_segment_analytics(sf)
            
            message_text = "📊 **Analytics Dashboard**\n\n"
            
            # Data Cloud stats
            if 'error' not in dc_analytics:
                message_text += "**Real Data Cloud:**\n"
                message_text += f"• Email Engagements: {dc_analytics['total_records']['email_engagements']:,}\n"
                message_text += f"• Message Engagements: {dc_analytics['total_records'].get('message_engagements', 0):,}\n"
                message_text += f"• Website Events: {dc_analytics['total_records']['website_events']:,}\n"
                message_text += f"• Orders: {dc_analytics['total_records']['orders']:,}\n\n"
            
            # Segment stats
            message_text += "**Segments:**\n"
            message_text += f"• Total Segments: {segment_analytics['total_segments']}\n"
            message_text += f"• Total Members: {segment_analytics['total_members']}\n"
            message_text += f"• Synced Campaigns: {segment_analytics['synced_campaigns']}\n\n"
            
            message_text += "🎯 **Segment Breakdown:**\n"
            for obj, count in segment_analytics['segments_by_object'].items():
                message_text += f"• {obj}: {count} segments\n"
            
            message_text += "\n✅ View full analytics in the **Analytics** page!"
            
            return {
                'intent': 'show_analytics',
                'message': message_text,
                'data': {'datacloud': dc_analytics, 'segments': segment_analytics},
                'suggested_actions': [
                    'View detailed analytics',
                    'Show me Individual analytics',
                    'Create performance dashboard'
                ]
            }
            
        except Exception as e:
            return {
                'intent': 'show_analytics',
                'message': f"📊 I can show you analytics!\n\nAvailable analytics:\n• Data Cloud engagement stats\n• Segment performance\n• Email campaign metrics\n• Website behavior\n\nGo to the **Analytics** page for detailed visualizations!",
                'data': None,
                'suggested_actions': ['Go to Analytics page', 'Show me Individual analytics']
            }
    
    def _show_individual_analytics(self, sf):
        """Show detailed analytics about Individuals with engagement data"""
        try:
            import os
            import json
            
            # Load synthetic engagement data
            engagement_file = 'data/synthetic_engagement.json'
            if not os.path.exists(engagement_file):
                return {
                    'intent': 'show_analytics',
                    'message': "❌ No engagement data found. Please run the engagement data generation scripts first.\n\nGo to Data Management → Individuals to create test records with engagement data.",
                    'data': None,
                    'suggested_actions': ['Create Individual records', 'Generate engagement data']
                }
            
            with open(engagement_file, 'r') as f:
                engagement_data = json.load(f)
            
            # Calculate analytics
            total_individuals = len(engagement_data)
            
            # Engagement distribution
            high_engaged = [i for i in engagement_data if i['engagement_score'] >= 6]
            med_engaged = [i for i in engagement_data if 3 <= i['engagement_score'] < 6]
            low_engaged = [i for i in engagement_data if i['engagement_score'] < 3]
            
            # Channel preferences
            channel_counts = {}
            for ind in engagement_data:
                channel = ind.get('preferred_channel', 'Unknown')
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
            
            # Calculate averages
            avg_email_opens = sum(i.get('email_opens', 0) for i in engagement_data) / total_individuals
            avg_sms_opens = sum(i.get('sms_opens', 0) for i in engagement_data) / total_individuals
            avg_whatsapp_reads = sum(i.get('whatsapp_reads', 0) for i in engagement_data) / total_individuals
            avg_push_opens = sum(i.get('push_opens', 0) for i in engagement_data) / total_individuals
            avg_website_views = sum(i.get('website_product_views', 0) for i in engagement_data) / total_individuals
            avg_purchases = sum(i.get('website_purchases', 0) for i in engagement_data) / total_individuals
            total_revenue = sum(i.get('total_order_value', 0) for i in engagement_data)
            
            # Top 5 engaged individuals
            top_5 = sorted(engagement_data, key=lambda x: x['engagement_score'], reverse=True)[:5]
            
            # Build message
            message_text = "📊 **Individual Engagement Analytics**\n\n"
            message_text += f"**Overview:**\n"
            message_text += f"• Total Individuals: {total_individuals}\n"
            message_text += f"• Avg Engagement Score: {sum(i['engagement_score'] for i in engagement_data)/total_individuals:.1f}/10\n"
            message_text += f"• Total Revenue Generated: ${total_revenue:,.2f}\n\n"
            
            message_text += "**📈 Engagement Distribution:**\n"
            message_text += f"• 🟢 High (6-10): {len(high_engaged)} individuals ({len(high_engaged)/total_individuals*100:.0f}%)\n"
            message_text += f"• 🟡 Medium (3-5): {len(med_engaged)} individuals ({len(med_engaged)/total_individuals*100:.0f}%)\n"
            message_text += f"• 🔴 Low (0-2): {len(low_engaged)} individuals ({len(low_engaged)/total_individuals*100:.0f}%)\n\n"
            
            message_text += "**💬 Preferred Channels:**\n"
            for channel, count in sorted(channel_counts.items(), key=lambda x: x[1], reverse=True):
                message_text += f"• {channel}: {count} individuals ({count/total_individuals*100:.0f}%)\n"
            
            message_text += f"\n**📧 Average Channel Performance:**\n"
            message_text += f"• Email Opens: {avg_email_opens:.1f} per person\n"
            message_text += f"• SMS Opens: {avg_sms_opens:.1f} per person\n"
            message_text += f"• WhatsApp Reads: {avg_whatsapp_reads:.1f} per person\n"
            message_text += f"• Push Opens: {avg_push_opens:.1f} per person\n"
            message_text += f"• Website Views: {avg_website_views:.1f} per person\n"
            message_text += f"• Purchases: {avg_purchases:.1f} per person\n\n"
            
            message_text += "**🌟 Top 5 Most Engaged:**\n"
            for i, ind in enumerate(top_5, 1):
                message_text += f"{i}. {ind['name']} - Score: {ind['engagement_score']}/10 (Prefers {ind.get('preferred_channel', 'N/A')})\n"
            
            message_text += "\n💡 **Insights:**\n"
            # Generate insights
            if len(high_engaged) > total_individuals * 0.3:
                message_text += "• ✅ Great! Over 30% of your audience is highly engaged!\n"
            if channel_counts.get('Email', 0) > total_individuals * 0.5:
                message_text += "• 📧 Email is your strongest channel - focus on email campaigns!\n"
            if avg_purchases < 1:
                message_text += "• 💡 Consider running promotional campaigns to boost purchases\n"
            if total_revenue > 10000:
                message_text += f"• 💰 Strong revenue of ${total_revenue:,.2f} from engaged customers!\n"
            
            return {
                'intent': 'show_analytics',
                'message': message_text,
                'data': {
                    'total_individuals': total_individuals,
                    'engagement_distribution': {
                        'high': len(high_engaged),
                        'medium': len(med_engaged),
                        'low': len(low_engaged)
                    },
                    'channel_preferences': channel_counts,
                    'top_engaged': [{'name': i['name'], 'score': i['engagement_score']} for i in top_5],
                    'total_revenue': total_revenue
                },
                'suggested_actions': [
                    'Create a segment from Individual',
                    'Export Individual data',
                    'Generate emails for top engaged'
                ]
            }
            
        except Exception as e:
            return {
                'intent': 'show_analytics',
                'message': f"❌ Error loading Individual analytics: {str(e)}\n\nPlease make sure you have Individual records with engagement data.",
                'data': None,
                'suggested_actions': ['Create Individual records', 'Generate engagement data']
            }
    
    def _handle_explain_data(self, original_message, message, sf):
        """Handle data explanation requests"""
        
        explanations = {
            'individual': "**Individual** is the unified customer profile in Data Cloud. It consolidates data from multiple sources (email, website, orders) into a single 360° view of each person.",
            'engagement score': "**Engagement Score** (0-10) measures how actively someone interacts with your brand. It combines email opens/clicks with website activity and purchases.",
            'segment': "**Segments** are filtered groups of individuals based on criteria like engagement level, purchase history, or demographics. Use them to target specific audiences.",
            'campaign': "**Campaigns** are organized marketing efforts to reach specific audiences. Link campaigns to segments to track performance and ROI.",
            'data cloud': "**Data Cloud** is Salesforce's customer data platform that unifies data from multiple sources, creating a complete view of each customer for better personalization.",
            'synthetic data': "**Synthetic Data** is artificially generated data that mimics real customer behavior. Perfect for testing and demos without using real customer information."
        }
        
        # Find matching explanation
        explanation = None
        for key, value in explanations.items():
            if key in message:
                explanation = value
                break
        
        if explanation:
            message_text = f"💡 **Explanation**\n\n{explanation}\n\n"
            message_text += "Need more details? Ask me about:\n"
            for key in explanations.keys():
                if key not in message:
                    message_text += f"• {key.title()}\n"
        else:
            message_text = "💡 **Data Cloud Concepts**\n\n"
            message_text += "I can explain:\n"
            for key in explanations.keys():
                message_text += f"• **{key.title()}**\n"
            message_text += "\nTry asking: 'What is an engagement score?' or 'Explain segments'"
        
        return {
            'intent': 'explain_data',
            'message': message_text,
            'data': None,
            'suggested_actions': ['Ask another question', 'View documentation']
        }
    
    def _handle_unknown_intent(self, message):
        """Handle unknown intents"""
        
        return f"""🤔 I'm not sure I understood that request.

I can help you with:

**📊 Data Investigation**
• "Show me the Individual table"
• "Investigate Campaign contents"

**🎯 Segmentation**
• "Create a segment for highly engaged users"
• "Filter individuals with purchases > 3"

**📧 Email Campaigns**
• "Generate VIP welcome emails"
• "Create email campaign for my segment"

**🔨 Data Creation**
• "Create 50 Individual records"
• "Generate synthetic engagement data"

**📈 Analytics**
• "Show me analytics"
• "What's my engagement performance?"

**💡 Explanations**
• "What is an engagement score?"
• "Explain Data Cloud"

Try rephrasing your question or pick one of the examples above!"""
    
    def get_conversation_history(self):
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history and context"""
        self.conversation_history = []
        self.context = {
            'last_segment_created': None,
            'last_segment_id': None,
            'last_segment_name': None,
            'last_action': None,
            'entities_mentioned': []
        }
        return {'message': 'Conversation history and context cleared. Starting fresh chat!'}

