#!/usr/bin/env python3
"""
Personalized Image Generator using Fal.ai
Generates campaign images with face-swap based on individual profiles and segments
"""

import os
import json
import base64
import io
from PIL import Image
import requests
import cloudinary
import cloudinary.uploader
import replicate

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
        
        # Activity-specific scenarios with FULL personalization
        activity_scenarios = {
            'Hiking': f"Professional action photograph of athletic person hiking on a scenic mountain trail during golden hour, wearing premium {favourite_brand} outdoor gear and hiking boots, {sentiment_mood} expression, {destination_background} in the background, {lifestyle.lower()} adventure lifestyle aesthetic, achieving {fitness_milestone}, photorealistic, high-quality outdoor photography, cinematic lighting",
            
            'Running': f"Dynamic action shot of fit athletic person powerfully exercising on {favourite_exercise.lower()} in an ultra-modern luxury gym, wearing stylish {favourite_brand} athletic wear, {sentiment_mood} expression showing determination, large windows revealing {destination_background}, state-of-the-art fitness equipment visible, {lifestyle.lower()} lifestyle aesthetic, achieving {fitness_milestone} goal, professional fitness photography, dramatic gym lighting with natural light streaming in, photorealistic, 8K quality",
            
            'Yoga': f"Serene photograph of person in perfect yoga pose on an exclusive rooftop studio or beach, wearing elegant {favourite_brand} yoga outfit, {sentiment_mood} and mindful expression, {destination_background} creating a stunning backdrop, sunrise or sunset golden hour lighting, {lifestyle.lower()} wellness lifestyle, celebrating {fitness_milestone}, zen and peaceful atmosphere, professional wellness photography, highly detailed",
            
            'Cycling': f"Epic action shot of cyclist riding a premium road bike on a scenic route, wearing professional {favourite_brand} cycling gear and helmet, {sentiment_mood} and focused, {destination_background} landscape surrounding them, {lifestyle.lower()} athletic lifestyle, achieving {fitness_milestone}, dynamic motion blur on wheels, professional cycling photography, golden hour lighting",
            
            'Swimming': f"Professional photograph of swimmer in a luxurious infinity pool, wearing {favourite_brand} swimwear, {sentiment_mood} expression, {destination_background} creating stunning views, {lifestyle.lower()} lifestyle aesthetic, celebrating {fitness_milestone}, crystal clear water, natural lighting, resort photography quality",
            
            'Reading': f"Sophisticated photograph of person reading in an elegant setting - luxury lounge or cafe, wearing casual {favourite_brand} lifestyle clothing, {sentiment_mood} and relaxed, {destination_background} visible through windows, {lifestyle.lower()} intellectual lifestyle, cozy atmospheric lighting, high-end lifestyle photography, warm tones",
            
            'Photography': f"Creative portrait of photographer with professional camera equipment, wearing {favourite_brand} gear, {sentiment_mood} and passionate expression, actively photographing {destination_background}, {lifestyle.lower()} creative lifestyle, artistic composition, professional lifestyle photography, natural lighting",
            
            'Cooking': f"Professional culinary photograph of person preparing gourmet cuisine in a modern luxury kitchen, wearing {favourite_brand} chef attire or apron, {sentiment_mood} and passionate, kitchen with view of {destination_background}, {lifestyle.lower()} lifestyle aesthetic, premium cookware and ingredients visible, warm atmospheric lighting, food photography quality"
        }
        
        # Check if there's an upcoming event to incorporate
        event_context = ""
        if upcoming_event and upcoming_event != 'None':
            event_context = f" preparing for upcoming {upcoming_event},"
        
        # Get activity-specific scenario or create comprehensive default
        base_scenario = activity_scenarios.get(hobby, 
            f"Professional lifestyle photograph of athletic person engaged in {hobby.lower()}{event_context} wearing premium {favourite_brand} apparel and gear, {sentiment_mood} expression, {destination_background} in the background, {lifestyle.lower()} lifestyle aesthetic, achieving {fitness_milestone}, high-quality commercial photography, photorealistic, dramatic lighting"
        )
        
        # Add upcoming event emphasis if present
        if upcoming_event and upcoming_event != 'None':
            base_scenario += f" Image should convey preparation and excitement for {upcoming_event} event."
        
        return base_scenario
    
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
            
            return {
                'success': True,
                'image_url': final_image_url,
                'base_image_url': target_image_url,
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

