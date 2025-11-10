#!/usr/bin/env python3
"""
Add profile pictures to all 100 synthetic profiles
- Biswarup Banerjee: Use uploaded photo
- Others: Generate DiceBear avatar URLs
"""

import json
import os
import urllib.parse

def generate_avatar_url(name, style='avataaars'):
    """
    Generate DiceBear avatar URL
    Styles: avataaars, bottts, initials, personas, identicon, lorelei
    """
    # URL encode the name to use as seed
    seed = urllib.parse.quote(name)
    return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"

def add_profile_pictures():
    """Add profile_picture_url to all profiles"""
    
    # Path to synthetic engagement data
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'synthetic_engagement.json')
    
    print("="*80)
    print("ADDING PROFILE PICTURES TO SYNTHETIC PROFILES")
    print("="*80)
    
    # Load existing data
    print(f"\n→ Loading data from {data_file}...")
    with open(data_file, 'r') as f:
        profiles = json.load(f)
    
    print(f"✅ Loaded {len(profiles)} profiles\n")
    
    # Mix of avatar styles for variety
    styles = ['avataaars', 'bottts', 'personas', 'lorelei', 'initials']
    
    updated_count = 0
    
    for idx, profile in enumerate(profiles):
        name = profile.get('Name', '')
        
        if name == 'Biswarup Banerjee':
            # Use uploaded photo for Biswarup
            profile['profile_picture_url'] = '/static/images/biswarup_banerjee.jpg'
            print(f"✓ {name}: Using uploaded photo")
        else:
            # Generate avatar URL with rotating styles for variety
            style = styles[idx % len(styles)]
            avatar_url = generate_avatar_url(name, style)
            profile['profile_picture_url'] = avatar_url
            print(f"✓ {name}: Generated {style} avatar")
        
        updated_count += 1
    
    # Save updated data
    print(f"\n→ Saving updated profiles...")
    with open(data_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    print(f"✅ Successfully added profile pictures to {updated_count} profiles!")
    print(f"📁 Data saved to: {data_file}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total profiles updated: {updated_count}")
    print(f"  • Biswarup Banerjee: Custom photo (/static/images/biswarup_banerjee.jpg)")
    print(f"  • Others: DiceBear avatars (mixed styles)")
    print("\nNext step: Update UI to display these profile pictures!")

if __name__ == '__main__':
    add_profile_pictures()

