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
        """Generate personalized scenario prompt based on individual's profile"""
        
        name = individual_data.get('Name', 'person')
        
        # Get insights data
        fitness_milestone = individual_data.get('fitness_milestone', 'beginner')
        favourite_brand = individual_data.get('favourite_brand', 'Nike')
        favourite_destination = individual_data.get('favourite_destination', 'beach')
        hobby = individual_data.get('hobby', 'running')
        lifestyle = individual_data.get('lifestyle_quotient', 'Active')
        sentiment = individual_data.get('current_sentiment', 'Happy')
        
        # Map hobbies/preferences to scenarios
        scenario_templates = {
            'Hiking': f"Professional photo of person hiking on a scenic mountain trail, wearing {favourite_brand} gear, beautiful landscape in background, golden hour lighting, adventure lifestyle photography",
            'Running': f"Action shot of person running on a modern treadmill in a premium gym, wearing {favourite_brand} athletic wear, energetic and focused expression, bright gym lighting, fitness motivation",
            'Yoga': f"Person doing yoga pose on a peaceful beach at sunrise, wearing {favourite_brand} yoga outfit, serene ocean view, wellness and mindfulness theme",
            'Cycling': f"Person cycling on a scenic road with {favourite_destination} landscape in background, wearing professional {favourite_brand} cycling gear, dynamic action shot",
            'Swimming': f"Person swimming in crystal clear pool, professional swimmer aesthetic, {favourite_brand} swimwear, refreshing and energetic vibe",
            'Reading': f"Person relaxing with a book in a cozy {favourite_destination}-style setting, sophisticated and peaceful atmosphere, warm lighting",
            'Photography': f"Person with professional camera equipment, exploring {favourite_destination}, creative photographer aesthetic, {favourite_brand} gear visible",
            'Cooking': f"Person in modern kitchen preparing gourmet meal, professional chef aesthetic, {favourite_brand} cookware, warm inviting atmosphere"
        }
        
        # Default scenario
        default_scenario = f"Professional lifestyle photo of person engaged in {hobby.lower()}, wearing {favourite_brand} apparel, {lifestyle.lower()} lifestyle aesthetic, high-quality commercial photography"
        
        scenario = scenario_templates.get(hobby, default_scenario)
        
        return scenario
    
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
            
            # Step 1: Generate base scene image with SDXL
            print("⚡ Step 1: Generating base scene with SDXL...")
            base_output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": scenario_prompt,
                    "width": 1024,
                    "height": 768,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                    "scheduler": "K_EULER"
                }
            )
            
            # Get the generated image URL
            if isinstance(base_output, list) and len(base_output) > 0:
                target_image_url = base_output[0]
            else:
                target_image_url = str(base_output)
            
            print(f"✅ Base scene generated: {target_image_url[:100]}...")
            
            # Step 2: Face-swap using Replicate's face-swap model
            print("🔄 Step 2: Swapping face with profile picture...")
            swap_output = replicate.run(
                "yan-ops/face_swap:d5900f9ebed33e7ae6f649a710feef37d71c0e03c53a8b0bc2b69a5c18dc036d",
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

