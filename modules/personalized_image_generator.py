#!/usr/bin/env python3
"""
Personalized Image Generator using Replicate API
Generates campaign images with face-swap based on individual profiles and segments
"""

import os
import json
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import requests
import cloudinary
import cloudinary.uploader
import replicate
import urllib.request

class PersonalizedImageGenerator:
    def __init__(self):
        self.fal_api_key = os.environ.get('FAL_KEY', '')
        self.replicate_api_key = os.environ.get('REPLICATE_API_TOKEN', '')
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'demo'),
            api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET', '')
        )
        
    def generate_personalized_image(self, individual_data, scenario_prompt=None):
        """
        Generate personalized campaign image for an individual
        
        Args:
            individual_data: Dict with individual's profile, insights, and preferences
            scenario_prompt: Optional custom scenario prompt
            
        Returns:
            Dict with generated image URL and metadata
        """
        
        # Extract profile picture
        profile_pic_url = individual_data.get('profile_picture_url', '')
        
        if not profile_pic_url:
            return {
                'success': False,
                'error': 'No profile picture available for this individual'
            }
        
        # Generate dynamic prompt based on individual's data
        if not scenario_prompt:
            scenario_prompt = self._generate_scenario_prompt(individual_data)
        
        # Call Replicate API for face-swap image generation
        try:
            result = self._call_fal_api(profile_pic_url, scenario_prompt, individual_data)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_scenario_prompt(self, individual_data):
        """Generate detailed, context-aware scenario prompts based on individual's profile"""
        
        # Extract all psychographic insights
        favourite_exercise = individual_data.get('favourite_exercise', 'Treadmill Running')
        favourite_brand = individual_data.get('favourite_brand', 'Nike')
        favourite_destination = individual_data.get('favourite_destination', 'Beach Resort')
        lifestyle = individual_data.get('lifestyle_quotient', 'Active')
        fitness_milestone = individual_data.get('fitness_milestone', 'Intermediate')
        sentiment = individual_data.get('current_sentiment', 'Motivated')
        upcoming_event = individual_data.get('upcoming_event', None)
        
        # Sentiment to mood mapping
        sentiment_moods = {
            'Motivated': 'energetic and determined',
            'Excited': 'joyful and enthusiastic',
            'Stressed': 'focused yet calm',
            'Relaxed': 'peaceful and content',
            'Confident': 'self-assured and powerful',
            'Happy': 'joyful and smiling',
            'Angry': 'intense and focused'
        }
        sentiment_mood = sentiment_moods.get(sentiment, 'determined')
        
        # Destination background mapping - NOW USED AS ACTUAL BACKGROUND (not through windows!)
        destination_backgrounds = {
            'Beach Resort': 'on pristine sandy beach with turquoise ocean waves and palm trees in the background',
            'Mountain Retreat': 'in mountain landscape with snow-capped peaks and alpine scenery behind',
            'Urban City': 'on modern city rooftop with glass skyscrapers visible in background',
            'Countryside': 'in countryside setting with rolling green hills and pastoral landscape',
            'Desert Oasis': 'in desert oasis with golden sand dunes and palm trees',
            'Tropical Island': 'in tropical paradise with lush jungle and waterfalls visible',
            'European Villa': 'at Mediterranean villa terrace with cypress trees and scenic views',
            'Asian Temple': 'at oriental temple courtyard with zen gardens and architecture',
            'Safari Lodge': 'in African savanna setting with acacia trees and wildlife',
            'Lakeside Cabin': 'beside serene mountain lake with pine forests in background',
            'Singapore': 'at scenic Singapore location with Marina Bay Sands visible in background',
            'Paris': 'at elegant Parisian location with Eiffel Tower visible in distance',
            'Tokyo': 'in modern Tokyo setting with cityscape in background',
            'New York': 'in New York City with Manhattan skyline visible',
            'London': 'in London with iconic architecture and Big Ben visible',
            'Dubai': 'in Dubai with luxurious skyline and Burj Khalifa',
            'Maldives': 'in Maldives paradise with crystal clear turquoise waters and overwater bungalows'
        }
        destination_background = destination_backgrounds.get(favourite_destination, f'in scenic {favourite_destination.lower()} setting')
        
        # Brand integration mapping - SPECIFIC to brand type
        tech_brands = ['Samsung', 'Bose', 'Garmin', 'Apple', 'Fitbit', 'Polar', 'JBL', 'Sony']
        apparel_brands = ['Nike', 'Adidas', 'Under Armour', 'Lululemon', 'Puma', 'Reebok', 'New Balance', 'Asics']
        non_fitness_brands = ['Netflix', 'Spotify', 'Amazon', 'Google', 'Microsoft', 'Facebook', 'Instagram', 'Twitter', 'YouTube', 'Airbnb', 'Uber']
        
        if favourite_brand in tech_brands:
            brand_detail = f"wearing {favourite_brand} smartwatch and wireless earbuds clearly visible on wrist and ears"
        elif favourite_brand in apparel_brands:
            brand_detail = f"wearing {favourite_brand} athletic wear with visible brand logo on chest"
        elif favourite_brand in non_fitness_brands:
            # If the brand isn't fitness-related, skip brand mention and use generic athletic wear
            brand_detail = f"wearing premium athletic fitness gear"
        else:
            # Unknown brand - keep it generic
            brand_detail = f"wearing premium athletic wear"
        
        # Add upcoming event context if present
        event_context = ''
        if upcoming_event and upcoming_event != 'None':
            event_context = f' preparing for {upcoming_event}'
        
        # Exercise-specific action descriptions
        exercise_actions = {
            'Treadmill Running': 'running on treadmill',
            'Yoga': 'doing yoga pose',
            'Cycling': 'cycling on bike',
            'Swimming': 'swimming',
            'Weight Lifting': 'lifting dumbbells',
            'HIIT Training': 'doing high-intensity training',
            'Pilates': 'doing pilates exercise',
            'Boxing': 'practicing boxing moves',
            'Dance Fitness': 'dancing energetically',
            'CrossFit': 'doing CrossFit workout',
            'Rowing': 'rowing',
            'Rock Climbing': 'rock climbing',
            'Martial Arts': 'practicing martial arts',
            'Tennis': 'playing tennis',
            'Basketball': 'playing basketball',
            'Soccer': 'playing soccer',
            'Golf': 'practicing golf swing',
            'Skiing': 'skiing',
            'Surfing': 'surfing',
            'Elliptical Training': 'training on elliptical',
            'Outdoor Jogging': 'jogging',
            'Rowing Machine': 'using rowing machine',
            'Stationary Bike': 'riding stationary bike',
            'Yoga Flow': 'doing yoga flow',
            'Squats': 'doing squats',
            'Bench Press': 'doing bench press'
        }
        
        action = exercise_actions.get(favourite_exercise, f'doing {favourite_exercise.lower()}')
        
        # GENERATE COMPLETE PROMPT - destination as actual background, no gym!
        personalized_scenario = (
            f"Professional fitness photograph of athletic person {action}{event_context}, "
            f"{destination_background}, "
            f"{brand_detail}, "
            f"{sentiment_mood} expression, "
            f"{lifestyle.lower()} lifestyle aesthetic, "
            f"natural outdoor lighting, photorealistic, high-resolution 8K quality, professional sports photography style"
        )
        
        return personalized_scenario
    
    def _call_fal_api(self, profile_pic_url, scenario_prompt, individual_data):
        """
        Generate personalized image with face-swap using Replicate API
        Two-step process: Generate base scene + Face-swap
        """
        
        if not self.replicate_api_key:
            return {
                'success': False,
                'error': 'REPLICATE_API_TOKEN not set. Please add it to Heroku config.'
            }
        
        print(f"🔑 Replicate API key present: {self.replicate_api_key[:10]}...")
        
        # Prepare the face image (convert base64 to public URL via Cloudinary)
        face_image_url = self._prepare_face_image(profile_pic_url)
        
        if not face_image_url or not face_image_url.startswith('http'):
            return {
                'success': False,
                'error': 'Could not prepare face image. Please ensure Cloudinary is configured or profile picture is a valid URL.'
            }
        
        # Two-step process for face-swap
        try:
            print(f"🎨 Starting face-swap generation for {individual_data.get('Name', 'Unknown')}")
            print(f"👤 Face image URL: {face_image_url[:100]}...")
            print(f"📝 Scenario: {scenario_prompt[:150]}...")
            
            # Step 1: Generate base scene image with SDXL
            print("⚡ Step 1: Generating base scene with SDXL...")
            
            # Enhanced prompt for better accuracy
            enhanced_prompt = f"{scenario_prompt}, professional photography, clear face details, accurate human anatomy, photorealistic skin texture, natural body proportions, realistic fitness setting"
            
            base_output = replicate.run(
                "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                input={
                    "prompt": enhanced_prompt,
                    "negative_prompt": "blurry, distorted face, wrong gender, cartoon, anime, low quality, bad anatomy, deformed, disfigured, poorly drawn face, mutation, gym, indoor, ceiling, roof",
                    "width": 1024,
                    "height": 768,
                    "num_inference_steps": 40,
                    "guidance_scale": 8.5
                }
            )
            
            # Get the generated image URL
            print(f"🔍 Base output type: {type(base_output)}")
            print(f"🔍 Base output value: {base_output}")
            
            if isinstance(base_output, list) and len(base_output) > 0:
                target_image_url = base_output[0]
            else:
                target_image_url = str(base_output)
            
            if not target_image_url or target_image_url == 'None':
                raise Exception(f"SDXL failed to generate base image. Output was: {base_output}")
            
            print(f"✅ Base scene generated: {target_image_url[:100]}...")
            
            # Step 2: Face-swap using Replicate's face-swap model
            print("🔄 Step 2: Swapping face with profile picture...")
            swap_output = replicate.run(
                "lucataco/faceswap:9a4298548422074c3f57258c5d544497314ae4112df80d116f0d2109e843d20d",
                input={
                    "target_image": target_image_url,
                    "swap_image": face_image_url
                }
            )
            
            # Get the face-swapped image URL
            print(f"🔍 Swap output type: {type(swap_output)}")
            print(f"🔍 Swap output value: {swap_output}")
            
            if isinstance(swap_output, list) and len(swap_output) > 0:
                final_image_url = swap_output[0]
            else:
                final_image_url = str(swap_output)
            
            if not final_image_url or final_image_url == 'None':
                # Face swap failed, but we have the base image
                print(f"⚠️ Face-swap failed, using base image instead")
                final_image_url = target_image_url
            
            print(f"🎉 Face-swap complete: {final_image_url[:100]}...")
            
            # Add promotional text overlay to the image
            try:
                final_image_with_text = self._add_promotional_overlay(final_image_url, individual_data)
                if final_image_with_text:
                    final_image_url = final_image_with_text
                    print(f"✅ Added promotional text overlay to image")
            except Exception as text_error:
                print(f"⚠️ Could not add text overlay: {text_error}")
            
            return {
                'success': True,
                'image_url': final_image_url,
                'base_image_url': target_image_url,
                'prompt_used': scenario_prompt,
                'prompt': scenario_prompt,
                'metadata': {
                    'model': 'replicate/sdxl + face_swap',
                    'individual': individual_data.get('Name', 'Unknown'),
                    'face_image': face_image_url[:100]
                }
            }
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Error during generation: {str(e)}")
            print(f"❌ Full traceback:")
            print(error_details)
            print(f"❌ Error type: {type(e).__name__}")
            print(f"❌ Error args: {e.args}")
            
            return {
                'success': False,
                'error': f'Replicate API error: {str(e)}',
                'details': error_details,
                'error_type': type(e).__name__
            }
    
    def _add_promotional_overlay(self, image_url, individual_data):
        """
        Add promotional text overlay to the generated image at the TOP
        Shows health alerts or promotional offers directly on the image
        """
        try:
            import requests
            from PIL import Image, ImageDraw, ImageFont
            from io import BytesIO
            import cloudinary.uploader
            
            # Check if we should add any promotional messages
            health_profile = individual_data.get('health_profile', individual_data.get('Health_Profile'))
            fitness_milestone = individual_data.get('fitness_milestone', individual_data.get('Fitness_Milestone'))
            
            # Determine what message to show
            message_text = None
            message_color = None
            
            # Priority 1: Health Alert (red) - for Hypertensive or any non-Fit/Healthy status
            if health_profile == 'Hypertensive':
                message_text = "⚕️ HEALTH ALERT: Please consult a doctor soon"
                message_color = (220, 53, 69)  # Red
            elif health_profile and health_profile not in ['Healthy', 'Fit', 'Active']:
                message_text = f"⚠️ Health Check: {health_profile} - Consult your doctor"
                message_color = (255, 152, 0)  # Orange
            # Priority 2: Fitness Milestone Offer (green) - for progression or Healthy/Fit
            elif health_profile in ['Healthy', 'Fit', 'Active'] and fitness_milestone in ['Advanced', 'Elite', 'Intermediate']:
                message_text = "🎉 50% OFF PREMIUM - Limited Time Offer!"
                message_color = (76, 175, 80)  # Green
            
            if not message_text:
                # No message to add
                return image_url
            
            # Download the image
            print(f"📥 Downloading image to add overlay...")
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            
            # Try to use a better font, fall back to default if not available
            try:
                # Use good-sized font for readability
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                except:
                    font = ImageFont.load_default()
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Wrap text to multiple lines if needed
            max_width = img_width - 80  # Leave 40px padding on each side
            lines = []
            
            # Simple word wrapping
            words = message_text.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]
                
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Single word is too long, add it anyway
                        lines.append(word)
                        current_line = ""
            
            if current_line:
                lines.append(current_line)
            
            # Calculate total text height for all lines
            line_height = 55  # Space between lines
            total_text_height = len(lines) * line_height
            
            # Create semi-transparent banner at TOP
            banner_height = total_text_height + 40
            banner_y = 0  # TOP of image
            
            # Draw semi-transparent rectangle at TOP
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(0, banner_y), (img_width, banner_height)],
                fill=message_color + (240,)  # Add alpha channel for semi-transparency
            )
            
            # Composite the overlay onto the original image
            img = img.convert('RGBA')
            img = Image.alpha_composite(img, overlay)
            img = img.convert('RGB')
            
            # Draw text on top - MULTI-LINE CENTERED in the banner
            draw = ImageDraw.Draw(img)
            
            # Start Y position (centered vertically in banner)
            start_y = 20
            
            # Draw each line centered
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = (img_width - line_width) // 2
                text_y = start_y + (i * line_height)
                
                # Add shadow for better readability
                shadow_offset = 2
                draw.text((text_x + shadow_offset, text_y + shadow_offset), line, fill='black', font=font)
                draw.text((text_x, text_y), line, fill='white', font=font)
            
            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # Upload the modified image back to Cloudinary
            print(f"☁️ Uploading image with overlay to Cloudinary...")
            result = cloudinary.uploader.upload(
                output,
                folder="personalized_images_with_text",
                resource_type="image"
            )
            
            modified_url = result.get('secure_url')
            print(f"✅ Image with overlay uploaded: {modified_url[:100]}...")
            
            return modified_url
            
        except Exception as e:
            print(f"⚠️ Error adding promotional overlay: {e}")
            import traceback
            print(traceback.format_exc())
            # Return original image if overlay fails
            return image_url
    
    def _prepare_face_image(self, profile_pic_url):
        """
        Prepare face image for Replicate API
        Convert base64 to public URL using Cloudinary
        """
        
        # If it's already a URL, return it
        if profile_pic_url.startswith('http'):
            return profile_pic_url
        
        # If it's a base64 data URI, upload to Cloudinary for public access
        if profile_pic_url.startswith('data:image'):
            try:
                # Upload to Cloudinary
                print("📤 Uploading base64 image to Cloudinary...")
                result = cloudinary.uploader.upload(
                    profile_pic_url,
                    folder="profile_pictures",
                    resource_type="image",
                    transformation=[
                        {'width': 512, 'height': 512, 'crop': 'fill', 'gravity': 'face'}
                    ]
                )
                uploaded_url = result.get('secure_url')
                print(f"✅ Uploaded successfully: {uploaded_url}")
                return uploaded_url
                
            except Exception as e:
                print(f"❌ Error uploading image: {e}")
                return profile_pic_url
        
        return profile_pic_url
    
    def generate_campaign_batch(self, segment_data, individuals_data, max_images=10):
        """
        Generate personalized images for a batch of individuals in a segment
        """
        results = []
        
        for idx, individual in enumerate(individuals_data[:max_images]):
            print(f"Generating image {idx+1}/{min(len(individuals_data), max_images)} for {individual.get('Name', 'Unknown')}")
            
            result = self.generate_personalized_image(individual)
            result['individual_name'] = individual.get('Name', 'Unknown')
            result['individual_id'] = individual.get('Id', '')
            
            results.append(result)
        
        return results
    
    def get_scenario_suggestions(self, individual_data):
        """Get AI-powered scenario suggestions based on individual's profile"""
        
        hobby = individual_data.get('hobby', 'running')
        brand = individual_data.get('favourite_brand', 'Nike')
        destination = individual_data.get('favourite_destination', 'beach')
        
        suggestions = [
            f"Action shot doing {hobby} with {brand} gear",
            f"Relaxing at {destination} destination",
            f"Professional lifestyle photo with {brand} products",
            f"Celebratory moment after achieving fitness goal",
            f"Training montage in modern environment"
        ]
        
        return suggestions
