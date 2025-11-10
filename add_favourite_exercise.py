#!/usr/bin/env python3
"""
Add Favourite_Exercise field to all individual insights
Also detect fitness milestone progressions for promotional offers
"""

import json
import random

# Load the insights data
with open('data/individual_insights.json', 'r') as f:
    insights = json.load(f)

# Diverse exercise options for fitness enthusiasts
exercises = [
    'Treadmill Running',
    'Rowing Machine',
    'Bench Press',
    'Squats',
    'Deadlifts',
    'Cycling',
    'Elliptical',
    'Battle Ropes',
    'Kettlebell Swings',
    'Pull-ups',
    'Push-ups',
    'Yoga Flow',
    'HIIT Circuit',
    'Boxing',
    'Pilates',
    'Swimming',
    'Rock Climbing',
    'CrossFit'
]

# Track each individual's exercises across time
individual_exercises = {}

# Update each insight record
for insight in insights:
    individual_id = insight.get('Individual_Id')
    
    # Assign consistent exercise per individual (not random each time)
    if individual_id not in individual_exercises:
        # Choose based on their hobby
        hobby = insight.get('Hobby', 'Running')
        
        # Map hobbies to likely favorite exercises
        if hobby == 'Running':
            individual_exercises[individual_id] = random.choice(['Treadmill Running', 'Elliptical', 'HIIT Circuit'])
        elif hobby == 'Cycling':
            individual_exercises[individual_id] = random.choice(['Cycling', 'Rowing Machine', 'Elliptical'])
        elif hobby == 'Yoga':
            individual_exercises[individual_id] = random.choice(['Yoga Flow', 'Pilates', 'Stretching'])
        elif hobby == 'Hiking':
            individual_exercises[individual_id] = random.choice(['Treadmill Running', 'Squats', 'Rock Climbing'])
        elif hobby == 'Swimming':
            individual_exercises[individual_id] = random.choice(['Swimming', 'Rowing Machine', 'Battle Ropes'])
        elif hobby == 'Reading':
            individual_exercises[individual_id] = random.choice(['Yoga Flow', 'Walking', 'Light Cardio'])
        else:
            individual_exercises[individual_id] = random.choice(exercises)
    
    # Add the Favourite_Exercise field
    insight['Favourite_Exercise'] = individual_exercises[individual_id]

# Save updated insights
with open('data/individual_insights.json', 'w') as f:
    json.dump(insights, f, indent=2)

print(f"✅ Added Favourite_Exercise to {len(insights)} insight records")
print(f"📊 {len(individual_exercises)} unique individuals have exercises assigned")
print("\nSample exercises assigned:")
for i, (ind_id, exercise) in enumerate(list(individual_exercises.items())[:10]):
    print(f"  - Individual {ind_id[:10]}...: {exercise}")

