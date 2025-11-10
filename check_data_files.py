#!/usr/bin/env python3
"""
Ensure data files exist on startup
If they don't exist, copy from seed files
This allows user uploads to persist while having initial data available
"""

import os
import shutil

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

if __name__ == '__main__':
    ensure_data_files()

