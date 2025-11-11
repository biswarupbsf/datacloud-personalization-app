#!/usr/bin/env python3
"""
Personalized Image Generator using Fal.ai
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
        
        # Call Fal.ai API for face-swap image generation
        try:
            result = self._call_fal_api(profile_pic_url, scenario_prompt, individual_data)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_scenario_prompt(self, individual_data):
        """
        Generate HYPER-PERSONALIZED scenario prompt based on ALL psychographic insights
        Dynamically incorporates: hobby, brand, destination, lifestyle, fitness, sentiment, events
        """
        
        name = individual_data.get('Name', 'person')
        
        # Get ALL psychographic insights
        fitness_milestone = individual_data.get('fitness_milestone', 'Active Lifestyle')
        favourite_brand = individual_data.get('favourite_brand', 'Nike')
        favourite_destination = individual_data.get('favourite_destination', 'Singapore')
        hobby = individual_data.get('hobby', 'Running')
        lifestyle = individual_data.get('lifestyle_quotient', 'Active')
        sentiment = individual_data.get('current_sentiment', 'Motivated')
        upcoming_event = individual_data.get('upcoming_event', None)
        favourite_exercise = individual_data.get('favourite_exercise', 'Treadmill Running')
        
        # Sentiment-to-mood mapping for more nuanced imagery
        sentiment_mood = {
            'Happy': 'joyful, smiling, celebrating',
            'Excited': 'energetic, enthusiastic, dynamic',
            'Motivated': 'focused, determined, powerful',
            'Relaxed': 'calm, peaceful, serene',
            'Confident': 'strong, assured, professional'
        }.get(sentiment, 'energetic and positive')
        
        # Destination-specific background elements
        destination_elements = {
            'Singapore': 'iconic Singapore skyline with Marina Bay Sands visible through floor-to-ceiling windows',
            'Paris': 'elegant Parisian architecture or Eiffel Tower in the distance',
            'Tokyo': 'modern Tokyo cityscape with neon lights',
            'New York': 'Manhattan skyline visible in background',
            'London': 'classic London architecture, Big Ben or London Eye visible',
            'Dubai': 'luxurious Dubai skyline with Burj Khalifa',
            'Beach': 'pristine beach with crystal clear water and palm trees',
            'Mountains': 'majestic mountain range with snow-capped peaks'
        }
        destination_background = destination_elements.get(favourite_destination, f'scenic {favourite_destination} landscape')
        
        # FITNESS EXERCISE-specific scenarios with FULL personalization
        # Map exercises to activity types
        exercise_scenarios = {
            # Treadmill & Running
            'Treadmill Running': f"Dynamic fitness photograph of athletic person powerfully running on treadmill in ultra-modern luxury gym, wearing {favourite_brand} athletic wear, {sentiment_mood} and focused expression, large windows revealing {destination_background}, state-of-the-art fitness equipment visible, {lifestyle.lower()} lifestyle aesthetic, achieving {fitness_milestone}, professional fitness photography, dramatic gym lighting, photorealistic",
            'Outdoor Jogging': f"Action shot of runner jogging on scenic path, wearing {favourite_brand} running gear, {sentiment_mood}, {destination_background} surrounding them, {lifestyle.lower()} active lifestyle, achieving {fitness_milestone}, golden hour outdoor lighting, professional sports photography",
            'Sprint Intervals': f"Intense fitness photo of person doing sprint training on track, wearing {favourite_brand} performance gear, {sentiment_mood} and powerful, {destination_background} in distance, {lifestyle.lower()} athletic lifestyle, achieving {fitness_milestone}, motion blur effect, professional sports photography",
            
            # Gym Equipment
            'Elliptical': f"Fitness photograph of person exercising on elliptical machine in modern gym, wearing {favourite_brand} athletic apparel, {sentiment_mood}, windows showing {destination_background}, {lifestyle.lower()} lifestyle, achieving {fitness_milestone}, professional gym photography, natural lighting",
            'Rowing Machine': f"Dynamic shot of athletic person using rowing machine in premium gym, wearing {favourite_brand} fitness wear, {sentiment_mood} and determined, {destination_background} visible through windows, {lifestyle.lower()} lifestyle, achieving {fitness_milestone}, professional fitness photography",
            'Stair Climber': f"Fitness photo of person on stair climber in modern gym, wearing {favourite_brand} athletic gear, {sentiment_mood}, large windows with {destination_background}, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional gym photography",
            
            # Strength Training  
            'Weight Lifting': f"Powerful photograph of person lifting weights in premium gym, wearing {favourite_brand} fitness apparel, {sentiment_mood} and strong, {destination_background} through floor-to-ceiling windows, {lifestyle.lower()} lifestyle, achieving {fitness_milestone}, professional strength training photography, dramatic lighting",
            'Squats': f"Fitness photo of person doing squats with proper form in modern gym, wearing {favourite_brand} workout clothes, {sentiment_mood}, {destination_background} visible, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional training photography",
            'Bench Press': f"Strength training photograph of person on bench press in high-end gym, wearing {favourite_brand} athletic wear, {sentiment_mood} and focused, {destination_background} through windows, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional gym photography",
            
            # Cycling
            'Cycling': f"Epic action shot of cyclist on premium road bike, wearing professional {favourite_brand} cycling gear, {sentiment_mood}, {destination_background} landscape, {lifestyle.lower()} athletic lifestyle, {fitness_milestone}, motion blur, professional cycling photography, golden hour",
            'Spin Class': f"Energetic photo of person in spin class at luxury gym, wearing {favourite_brand} cycling gear, {sentiment_mood}, {destination_background} through windows, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional indoor cycling photography",
            'Stationary Bike': f"Fitness photo of person on stationary bike in modern gym, wearing {favourite_brand} workout apparel, {sentiment_mood}, windows showing {destination_background}, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional gym photography",
            
            # Yoga & Flexibility
            'Yoga Flow': f"Serene photo of person in yoga pose at exclusive studio, wearing elegant {favourite_brand} yoga outfit, {sentiment_mood} and mindful, {destination_background} backdrop, sunrise lighting, {lifestyle.lower()} wellness lifestyle, {fitness_milestone}, professional yoga photography",
            'Pilates': f"Elegant photo of person doing Pilates in luxury studio, wearing {favourite_brand} activewear, {sentiment_mood}, {destination_background} visible, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional wellness photography",
            'Stretching': f"Peaceful photo of person stretching in modern gym or studio, wearing {favourite_brand} athletic wear, {sentiment_mood} and relaxed, {destination_background} through windows, {lifestyle.lower()} lifestyle, {fitness_milestone}, natural lighting",
            
            # Swimming
            'Swimming': f"Professional photo of swimmer in luxurious infinity pool, wearing {favourite_brand} swimwear, {sentiment_mood}, {destination_background} creating stunning views, {lifestyle.lower()} lifestyle, {fitness_milestone}, crystal clear water, natural lighting",
            'Water Aerobics': f"Fitness photo of person doing water aerobics in premium pool, wearing {favourite_brand} swimwear, {sentiment_mood}, {destination_background} visible, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional pool photography",
            
            # HIIT & Cross Training
            'HIIT Circuit': f"Intense fitness photo of person doing HIIT workout in modern gym, wearing {favourite_brand} performance gear, {sentiment_mood} and powerful, {destination_background} through windows, {lifestyle.lower()} athletic lifestyle, {fitness_milestone}, dynamic action shot",
            'Battle Ropes': f"Action shot of person using battle ropes in gym, wearing {favourite_brand} workout gear, {sentiment_mood} and fierce, {destination_background} visible, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional training photography",
            'Bodyweight Exercises': f"Fitness photo of person doing bodyweight training in gym or outdoor, wearing {favourite_brand} athletic apparel, {sentiment_mood}, {destination_background} setting, {lifestyle.lower()} lifestyle, {fitness_milestone}, professional fitness photography"
        }
        
        # Check if there's an upcoming event to incorporate
        event_context = ""
        if upcoming_event and upcoming_event != 'None':
            event_context = f" preparing for upcoming {upcoming_event},"
        
        # USE FAVOURITE EXERCISE (not hobby!) to determine the scenario
        base_scenario = exercise_scenarios.get(favourite_exercise, 
            f"Professional fitness photograph of athletic person doing {favourite_exercise.lower()}{event_context} wearing premium {favourite_brand} athletic apparel, {sentiment_mood} expression showing determination, {destination_background} visible through large windows, {lifestyle.lower()} lifestyle aesthetic, achieving {fitness_milestone} milestone, state-of-the-art gym setting, professional sports photography, photorealistic, dramatic lighting with natural light, 8K quality"
        )
        
        # Add upcoming event emphasis if present
        if upcoming_event and upcoming_event != 'None':
            base_scenario += f" Image should convey preparation and excitement for {upcoming_event} event."
        
        return base_scenario
    
    def _add_text_overlay(self, image_url, individual_data):
        """
        Add promotional text overlay to the generated image
        """
        try:
            # Download the image
            with urllib.request.urlopen(image_url) as url:
                img = Image.open(io.BytesIO(url.read()))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            
            # Determine promotional message
            health_profile = individual_data.get('health_profile', '')
            fitness_milestone = individual_data.get('fitness_milestone', '')
            
            # Check for health alert or promotional offer
            message = None
            bg_color = None
            
            if health_profile == 'Hypertensive':
                message = "⚕️ HEALTH ALERT: Schedule a consultation with your doctor"
                bg_color = (220, 53, 69, 230)  # Red with transparency
            else:
                # Check for fitness milestone progression (simplified check)
                if fitness_milestone in ['Elite', 'Advanced']:
                    message = "🎉 50% OFF Premium Membership - Limited Time!"
                    bg_color = (40, 167, 69, 230)  # Green with transparency
            
            if message:
                # Image dimensions
                width, height = img.size
                
                # Try to load a font (fallback to default if not available)
                try:
                    font_size = int(width * 0.025)  # 2.5% of image width
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Get text bounding box
                bbox = draw.textbbox((0, 0), message, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Position at bottom of image with padding
                padding = int(width * 0.02)
                text_x = (width - text_width) // 2
                text_y = height - text_height - padding * 2
                
                # Draw semi-transparent background rectangle
                rect_coords = [
                    text_x - padding,
                    text_y - padding,
                    text_x + text_width + padding,
                    text_y + text_height + padding
                ]
                
                # Create overlay for transparency
                overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle(rect_coords, fill=bg_color)
                
                # Composite overlay
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, overlay)
                img = img.convert('RGB')
                
                # Draw text
                draw = ImageDraw.Draw(img)
                draw.text((text_x, text_y), message, fill='white', font=font)
            
            # Save to BytesIO
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # Upload to Cloudinary with text overlay
            result = cloudinary.uploader.upload(
                output,
                folder="generated_images_with_text",
                resource_type="image"
            )
            
            return result.get('secure_url', image_url)
            
        except Exception as e:
            print(f"⚠️ Could not add text overlay: {e}")
            return image_url  # Return original image if overlay fails
    
    def _call_fal_api(self, profile_pic_url, scenario_prompt, individual_data):
        """
        Generate personalized image with face-swap using Replicate API
        Two-step process: Generate base scene + Face-swap
        """
        
        if not self.replicate_api_key:
            # Return mock response for testing without API key
            return {
                'success': False,
                'error': 'REPLICATE_API_TOKEN not set. Please add it to Heroku config.',
                'message': 'Sign up at https://replicate.com and get your API token',
                'metadata': {
                    'individual': individual_data.get('Name', 'Unknown')
                }
            }
        
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
            print(f"📝 Scenario: {scenario_prompt[:100]}...")
            
            # Step 1: Generate base scene image with SDXL (using latest version)
            print("⚡ Step 1: Generating base scene with SDXL...")
            base_output = replicate.run(
                "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                input={
                    "prompt": scenario_prompt,
                    "width": 1024,
                    "height": 768,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5
                }
            )
            
            # Get the generated image URL
            if isinstance(base_output, list) and len(base_output) > 0:
                target_image_url = base_output[0]
            else:
                target_image_url = str(base_output)
            
            print(f"✅ Base scene generated: {target_image_url[:100]}...")
            
            # Step 2: Face-swap using Replicate's face-swap model (updated version)
            print("🔄 Step 2: Swapping face with profile picture...")
            swap_output = replicate.run(
                "lucataco/faceswap:9a4298548422074c3f57258c5d544497314ae4112df80d116f0d2109e843d20d",
                input={
                    "target_image": target_image_url,
                    "swap_image": face_image_url
                }
            )
            
            # Get the face-swapped image URL
            if isinstance(swap_output, list) and len(swap_output) > 0:
                final_image_url = swap_output[0]
            else:
                final_image_url = str(swap_output)
            
            print(f"🎉 Face-swap complete: {final_image_url[:100]}...")
            
            # Add promotional overlay to the image
            final_image_with_text = self._add_promotional_overlay(final_image_url, individual_data)
            
            return {
                'success': True,
                'image_url': final_image_with_text if final_image_with_text else final_image_url,
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
            print(error_details)
            
            return {
                'success': False,
                'error': f'Replicate API error: {str(e)}',
                'details': error_details
            }
    
    def _add_promotional_overlay(self, image_url, individual_data):
        """
        Add promotional text overlay to the generated image
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
            elif health_profile and health_profile not in ['Healthy', 'Fit']:
                message_text = f"⚠️  Health Check: {health_profile} - Consult your doctor"
                message_color = (255, 152, 0)  # Orange
            # Priority 2: Fitness Milestone Offer (green) - for progression or Healthy/Fit
            elif health_profile in ['Healthy', 'Fit'] and fitness_milestone in ['Advanced', 'Elite', 'Intermediate']:
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
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
            except:
                font = ImageFont.load_default()
                font_small = font
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Calculate text size and position for banner at bottom
            bbox = draw.textbbox((0, 0), message_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Create semi-transparent banner at bottom
            banner_height = text_height + 40
            banner_y = img_height - banner_height
            
            # Draw semi-transparent rectangle
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(0, banner_y), (img_width, img_height)],
                fill=message_color + (230,)  # Add alpha channel for semi-transparency
            )
            
            # Composite the overlay onto the original image
            img = img.convert('RGBA')
            img = Image.alpha_composite(img, overlay)
            img = img.convert('RGB')
            
            # Draw text on top
            draw = ImageDraw.Draw(img)
            text_x = (img_width - text_width) / 2
            text_y = banner_y + 20
            
            # Draw text with shadow for better readability
            shadow_offset = 2
            draw.text((text_x + shadow_offset, text_y + shadow_offset), message_text, font=font, fill=(0, 0, 0))
            draw.text((text_x, text_y), message_text, font=font, fill=(255, 255, 255))
            
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
        Prepare face image for Fal.ai API
        Convert base64 to public URL using Cloudinary
        """
        
        # If it's already a URL, return it
        if profile_pic_url.startswith('http'):
            return profile_pic_url
        
        # If it's a base64 data URI, upload to Cloudinary for public access
        if profile_pic_url.startswith('data:image'):
            try:
                # Check if Cloudinary is configured
                if not os.environ.get('CLOUDINARY_API_KEY'):
                    print("⚠️ Cloudinary not configured - trying Fal.ai upload...")
                    # Fallback to Fal.ai upload
                    import fal_client
                    uploaded_url = fal_client.upload_file(profile_pic_url)
                    print(f"✅ Uploaded to Fal.ai: {uploaded_url}")
                    return uploaded_url
                
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
                # Last resort fallback to base64
                return profile_pic_url
        
        # If it's a local path, construct full URL
        if profile_pic_url.startswith('/static'):
            # This would be the Heroku app URL + static path
            base_url = os.environ.get('APP_URL', 'https://infinite-lowlands-00393-eacde66da597.herokuapp.com')
            return f"{base_url}{profile_pic_url}"
        
        return profile_pic_url
    
    def generate_campaign_batch(self, segment_data, individuals_data, max_images=10):
        """
        Generate personalized images for a batch of individuals in a segment
        
        Args:
            segment_data: Segment information
            individuals_data: List of individuals in the segment
            max_images: Maximum number of images to generate
            
        Returns:
            List of results for each individual
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
            f"Training montage in modern gym environment"
        ]
        
        return suggestions

