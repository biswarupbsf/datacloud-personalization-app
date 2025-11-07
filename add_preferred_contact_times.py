#!/usr/bin/env python3
"""
Add preferred contact times to synthetic engagement data
"""
import json
import random
from datetime import datetime

def add_preferred_contact_times():
    """Add preferred_contact_time field to engagement data"""
    
    # Define time windows that make sense for marketing
    time_windows = [
        "Early Morning (6-8 AM)",
        "Morning (8-10 AM)",
        "Late Morning (10-12 PM)",
        "Lunch Time (12-2 PM)",
        "Afternoon (2-4 PM)",
        "Late Afternoon (4-6 PM)",
        "Evening (6-8 PM)",
        "Night (8-10 PM)",
        "Late Night (10 PM-12 AM)"
    ]
    
    # Weighted preferences (some times are more popular)
    weights = [5, 15, 10, 8, 10, 12, 20, 15, 5]  # Evening and Night are most popular
    
    # Load engagement data
    with open('data/synthetic_engagement.json', 'r') as f:
        engagement_data = json.load(f)
    
    # Add preferred contact time to each individual
    for individual in engagement_data:
        # Assign a preferred contact time based on weighted random
        preferred_time = random.choices(time_windows, weights=weights)[0]
        individual['preferred_contact_time'] = preferred_time
    
    # Save updated data
    with open('data/synthetic_engagement.json', 'w') as f:
        json.dump(engagement_data, f, indent=2)
    
    print(f"✅ Added preferred_contact_time to {len(engagement_data)} individuals")
    
    # Show distribution
    time_distribution = {}
    for individual in engagement_data:
        time = individual['preferred_contact_time']
        time_distribution[time] = time_distribution.get(time, 0) + 1
    
    print("\n📊 Distribution of Preferred Contact Times:")
    for time, count in sorted(time_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"   {time}: {count} individuals")

if __name__ == '__main__':
    add_preferred_contact_times()

