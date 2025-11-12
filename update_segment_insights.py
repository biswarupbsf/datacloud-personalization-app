#!/usr/bin/env python3
"""
Update insights for the 5 segment members with diverse values
"""

import json
from datetime import datetime, timedelta

# Individual IDs for the 5 members
INDIVIDUAL_IDS = {
    "Biswarup Banerjee": "0PKKX000000Tfjv4AC",
    "Ashish Desai": "0PKKX000000Tfia4AC",
    "Deepika Chauhan": "0PKKX000000TfiZ4AS",
    "Rajesh Rao": "0PKKX000000TfiT4AS",
    "Archana Tripathi": "0PKKX000000Tfif4AC"
}

# Diverse values for each individual
SEGMENT_INSIGHTS = {
    "Biswarup Banerjee": {
        "Favourite_Exercise": "Treadmill Running",
        "Favourite_Brand": "Nike",  # Apparel brand
        "Favourite_Destination": "Singapore",
        "Hobby": "Running",
        "Health_Profile": "Fit",
        "Fitness_Milestone_Current": "Advanced",
        "Fitness_Milestone_Previous": "Intermediate",  # Shows progression
        "Lifestyle_Quotient": "Active",
        "Current_Sentiment": "Motivated",
        "Imminent_Event": "Marathon training next month"
    },
    "Ashish Desai": {
        "Favourite_Exercise": "Bench Press",
        "Favourite_Brand": "Samsung",  # Tech brand
        "Favourite_Destination": "Switzerland",
        "Hobby": "Cooking",
        "Health_Profile": "Healthy",
        "Fitness_Milestone_Current": "Elite",
        "Fitness_Milestone_Previous": "Advanced",  # Shows progression
        "Lifestyle_Quotient": "Minimalist",
        "Current_Sentiment": "Confident",
        "Imminent_Event": "Vacation to Switzerland next week"
    },
    "Deepika Chauhan": {
        "Favourite_Exercise": "CrossFit",
        "Favourite_Brand": "Garmin",  # Tech brand
        "Favourite_Destination": "Paris",
        "Hobby": "Dancing",
        "Health_Profile": "Healthy",
        "Fitness_Milestone_Current": "Intermediate",
        "Fitness_Milestone_Previous": "Beginner",  # Shows progression
        "Lifestyle_Quotient": "Connoisseur",
        "Current_Sentiment": "Excited",
        "Imminent_Event": "Dance competition this weekend"
    },
    "Rajesh Rao": {
        "Favourite_Exercise": "Yoga Flow",
        "Favourite_Brand": "Bose",  # Tech brand
        "Favourite_Destination": "Maldives",
        "Hobby": "Meditation",
        "Health_Profile": "Fit",
        "Fitness_Milestone_Current": "Elite",
        "Fitness_Milestone_Previous": "Advanced",  # Shows progression
        "Lifestyle_Quotient": "Luxury Seeker",
        "Current_Sentiment": "Relaxed",
        "Imminent_Event": "Yoga retreat in Maldives next month"
    },
    "Archana Tripathi": {
        "Favourite_Exercise": "Rock Climbing",
        "Favourite_Brand": "Adidas",  # Apparel brand
        "Favourite_Destination": "Maldives",
        "Hobby": "Playing Guitar",
        "Health_Profile": "Active",
        "Fitness_Milestone_Current": "Advanced",
        "Fitness_Milestone_Previous": "Intermediate",  # Shows progression
        "Lifestyle_Quotient": "Adventurer",
        "Current_Sentiment": "Happy",
        "Imminent_Event": "Vacation to Maldives next week"
    }
}

def update_insights():
    """Update insights for the 5 segment members"""
    
    insights_file = 'data/individual_insights.json'
    
    # Load existing insights
    with open(insights_file, 'r') as f:
        insights_data = json.load(f)
    
    # Get current timestamp
    now = datetime.now()
    
    # Update each individual
    for name, values in SEGMENT_INSIGHTS.items():
        individual_id = INDIVIDUAL_IDS[name]
        
        # Find existing insights for this individual
        existing_insights = [i for i in insights_data if i.get('Individual_Id') == individual_id]
        
        # Create new most recent insight with updated values
        new_insight = {
            "Individual_Id": individual_id,
            "Event_Timestamp": now.isoformat(),
            "Current_Sentiment": values["Current_Sentiment"],
            "Lifestyle_Quotient": values["Lifestyle_Quotient"],
            "Health_Profile": values["Health_Profile"],
            "Fitness_Milestone": values["Fitness_Milestone_Current"],
            "Purchase_Intent": "Very High",
            "Favourite_Brand": values["Favourite_Brand"],
            "Favourite_Destination": values["Favourite_Destination"],
            "Hobby": values["Hobby"],
            "Imminent_Event": values["Imminent_Event"],
            "Favourite_Exercise": values["Favourite_Exercise"],
            "data_source": "synthetic_insights",
            "Individual_Name": name,
            "Individual_FirstName": name.split()[0],
            "Individual_LastName": name.split()[1] if len(name.split()) > 1 else "",
            "Individual_Email": existing_insights[0].get('Individual_Email', '') if existing_insights else '',
            "Individual_Phone": existing_insights[0].get('Individual_Phone', '') if existing_insights else '',
            "InsightId": f"INSIGHT_{len(insights_data) + 1:04d}"
        }
        
        # Create previous insight with lower milestone (for progression detection)
        previous_timestamp = (now - timedelta(days=30)).isoformat()
        previous_insight = new_insight.copy()
        previous_insight["Event_Timestamp"] = previous_timestamp
        previous_insight["Fitness_Milestone"] = values["Fitness_Milestone_Previous"]
        previous_insight["InsightId"] = f"INSIGHT_{len(insights_data) + 2:04d}"
        
        # Add both insights (most recent first)
        insights_data.insert(0, new_insight)
        insights_data.insert(1, previous_insight)
        
        print(f"✅ Updated {name}:")
        print(f"   Exercise: {values['Favourite_Exercise']}")
        print(f"   Brand: {values['Favourite_Brand']}")
        print(f"   Destination: {values['Favourite_Destination']}")
        print(f"   Milestone: {values['Fitness_Milestone_Previous']} → {values['Fitness_Milestone_Current']}")
        print(f"   Health: {values['Health_Profile']}")
        print()
    
    # Save updated insights
    with open(insights_file, 'w') as f:
        json.dump(insights_data, f, indent=2)
    
    print(f"✅ Updated insights for all 5 segment members!")
    print(f"✅ Added milestone progression for each individual")

if __name__ == '__main__':
    update_insights()

