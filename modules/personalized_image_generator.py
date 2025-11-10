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

class PersonalizedImageGenerator:
    def __init__(self):
        self.fal_api_key = os.environ.get('FAL_API_KEY', '')
        
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
        Call Fal.ai API for face-swap image generation
        Using fal-ai/face-to-many model for realistic face insertion
        """
        
        if not self.fal_api_key:
            # Return mock response for testing without API key
            return {
                'success': True,
                'image_url': 'https://via.placeholder.com/512x512.png?text=Generated+Image',
                'prompt': scenario_prompt,
                'message': 'Demo mode - Add FAL_API_KEY environment variable for real generation',
                'metadata': {
                    'model': 'fal-ai/face-to-many',
                    'individual': individual_data.get('Name', 'Unknown')
                }
            }
        
        # Prepare the face image (convert base64 to URL if needed)
        face_image_url = self._prepare_face_image(profile_pic_url)
        
        # Call Fal.ai API
        try:
            import fal_client
            
            # Use face-to-many model for face swap
            result = fal_client.subscribe(
                "fal-ai/face-to-many",
                arguments={
                    "image_url": face_image_url,
                    "prompt": scenario_prompt,
                    "num_images": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 50,
                    "style": "Photographic"
                },
                with_logs=False,
            )
            
            if result and 'images' in result and len(result['images']) > 0:
                return {
                    'success': True,
                    'image_url': result['images'][0]['url'],
                    'prompt': scenario_prompt,
                    'metadata': {
                        'model': 'fal-ai/face-to-many',
                        'individual': individual_data.get('Name', 'Unknown'),
                        'seed': result.get('seed', None)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'No image generated by Fal.ai'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Fal.ai API error: {str(e)}'
            }
    
    def _prepare_face_image(self, profile_pic_url):
        """
        Prepare face image for Fal.ai API
        Convert base64 to temporary URL if needed
        """
        
        # If it's already a URL, return it
        if profile_pic_url.startswith('http'):
            return profile_pic_url
        
        # If it's a base64 data URI, we need to handle it
        if profile_pic_url.startswith('data:image'):
            # For now, return the base64 directly
            # Fal.ai accepts base64 data URIs
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

