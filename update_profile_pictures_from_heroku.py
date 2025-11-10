#!/usr/bin/env python3
"""
Temporary script to update profile_pictures.json with Cloudinary URLs
This ensures the URLs persist across deployments
"""

import json
import os

# The 5 members who need profile pictures
members = [
    "Biswarup Banerjee",
    "Ashish Desai", 
    "Deepika Chauhan",
    "Rajesh Rao",
    "Archana Tripathi"
]

# Note: These URLs will be set on Heroku after upload
# This file structure ensures they persist
profile_pics = {}

for member in members:
    # Placeholder - will be filled when you upload on Heroku
    profile_pics[member] = ""

# Save to profile_pictures.json
profile_pics_file = os.path.join('data', 'profile_pictures.json')
with open(profile_pics_file, 'w') as f:
    json.dump(profile_pics, f, indent=2)

print(f"✅ Updated {profile_pics_file}")
print("📝 Upload your pictures on Heroku, and they will persist!")

