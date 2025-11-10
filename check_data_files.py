#!/usr/bin/env python3
"""
Ensure data files exist on startup
If they don't exist, copy from seed files
Also restore profile pictures from persistent profile_pictures.json
"""

import os
import shutil
import json

def ensure_data_files():
    """Ensure data files exist, copy from seed if needed"""
    
    data_dir = 'data'
    seed_dir = os.path.join(data_dir, 'seed')
    
    files_to_check = [
        'synthetic_engagement.json',
        'individual_insights.json'
    ]
    
    for filename in files_to_check:
        data_file = os.path.join(data_dir, filename)
        seed_file = os.path.join(seed_dir, filename)
        
        if not os.path.exists(data_file):
            print(f"⚠️  {data_file} not found!")
            if os.path.exists(seed_file):
                print(f"✅ Copying from seed: {seed_file} -> {data_file}")
                shutil.copy2(seed_file, data_file)
            else:
                print(f"❌ ERROR: Seed file not found: {seed_file}")
        else:
            print(f"✅ {data_file} exists")
    
    # Restore profile pictures from persistent mapping
    restore_profile_pictures()

def restore_profile_pictures():
    """Restore profile picture URLs from persistent profile_pictures.json"""
    try:
        profile_pics_file = os.path.join('data', 'profile_pictures.json')
        engagement_file = os.path.join('data', 'synthetic_engagement.json')
        
        if not os.path.exists(profile_pics_file):
            print("⚠️  No profile_pictures.json found - skipping restore")
            return
        
        if not os.path.exists(engagement_file):
            print("⚠️  No synthetic_engagement.json found - skipping restore")
            return
        
        # Load profile pictures mapping
        with open(profile_pics_file, 'r') as f:
            profile_pics = json.load(f)
        
        # Load engagement data
        with open(engagement_file, 'r') as f:
            engagement_data = json.load(f)
        
        # Restore profile picture URLs
        restored_count = 0
        for person in engagement_data:
            name = person.get('Name')
            if name and name in profile_pics and profile_pics[name]:
                person['profile_picture_url'] = profile_pics[name]
                restored_count += 1
        
        # Save updated engagement data
        with open(engagement_file, 'w') as f:
            json.dump(engagement_data, f, indent=2)
        
        if restored_count > 0:
            print(f"✅ Restored {restored_count} profile pictures from persistent storage!")
        else:
            print("ℹ️  No profile pictures to restore")
            
    except Exception as e:
        print(f"⚠️  Error restoring profile pictures: {e}")

if __name__ == '__main__':
    ensure_data_files()

