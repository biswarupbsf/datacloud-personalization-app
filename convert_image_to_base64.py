#!/usr/bin/env python3
"""
Convert Biswarup's profile picture to base64 and embed it in the JSON data
This solves the Heroku ephemeral filesystem issue
"""

import json
import base64
import os

def image_to_base64(image_path):
    """Convert image to base64 data URI"""
    try:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            # Determine image type from file extension
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Create base64 data URI
            base64_data = base64.b64encode(img_data).decode('utf-8')
            data_uri = f"data:{mime_type};base64,{base64_data}"
            
            print(f"✅ Converted image to base64 ({len(base64_data)} chars)")
            return data_uri
    except Exception as e:
        print(f"❌ Error converting image: {e}")
        return None

def update_profile_with_base64():
    """Update Biswarup's profile with base64 image"""
    
    # Try to find the image
    image_paths = [
        'static/images/biswarup_banerjee.jpg',
        '../uploaded-person.jpg',
        'biswarup_banerjee.jpg'
    ]
    
    image_data_uri = None
    for path in image_paths:
        if os.path.exists(path):
            print(f"Found image at: {path}")
            image_data_uri = image_to_base64(path)
            if image_data_uri:
                break
    
    if not image_data_uri:
        print("❌ Could not find or convert image")
        print("Please upload the image using this script:")
        print("python3 convert_image_to_base64.py /path/to/your/image.jpg")
        return False
    
    # Update the JSON
    data_file = 'data/synthetic_engagement.json'
    try:
        with open(data_file, 'r') as f:
            profiles = json.load(f)
        
        updated = False
        for profile in profiles:
            if profile.get('Name') == 'Biswarup Banerjee':
                profile['profile_picture_url'] = image_data_uri
                print(f"✅ Updated {profile['Name']}'s profile with base64 image")
                updated = True
                break
        
        if updated:
            with open(data_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            print("✅ Saved to JSON successfully!")
            print("\n🚀 Now commit and deploy to Heroku!")
            return True
        else:
            print("❌ Could not find Biswarup Banerjee in profiles")
            return False
            
    except Exception as e:
        print(f"❌ Error updating JSON: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Custom image path provided
        custom_path = sys.argv[1]
        if os.path.exists(custom_path):
            data_uri = image_to_base64(custom_path)
            if data_uri:
                # Update JSON
                data_file = 'data/synthetic_engagement.json'
                with open(data_file, 'r') as f:
                    profiles = json.load(f)
                
                for profile in profiles:
                    if profile.get('Name') == 'Biswarup Banerjee':
                        profile['profile_picture_url'] = data_uri
                        print(f"✅ Updated profile with custom image")
                        break
                
                with open(data_file, 'w') as f:
                    json.dump(profiles, f, indent=2)
                print("✅ Done! Deploy to Heroku now.")
        else:
            print(f"❌ File not found: {custom_path}")
    else:
        update_profile_with_base64()

