"""
Module to generate synthetic Individual Insights data for Data Cloud
Tracks sentiment, lifestyle, health, fitness, purchase intent, and behavioral insights over time
"""
import random
import json
import os
from datetime import datetime, timedelta

class InsightsGenerator:
    def __init__(self):
        # Define value sets for each field
        self.sentiments = ['Happy', 'Sad', 'Elated', 'Frustrated', 'Disgusted', 'Angry', 'Excited', 'Anxious', 'Calm', 'Stressed']
        
        self.lifestyle_quotients = ['Careerist', 'Traveller', 'Foodie', 'Connoisseur', 'Homebody', 'Adventurer', 'Minimalist', 'Luxury Seeker', 'Health Enthusiast', 'Tech Savvy']
        
        self.health_profiles = ['Sick', 'Athletic', 'Stressed', 'Hypertensive', 'Hypotensive', 'Healthy', 'Recovering', 'Fit', 'Active', 'Sedentary']
        
        self.fitness_milestones = ['Rookie', 'Amateur', 'Professional', 'Elite', 'Beginner', 'Intermediate', 'Advanced', 'Champion']
        
        self.purchase_intents = ['Very High', 'Immediate', 'High', 'Medium', 'Tepid', 'Low', 'Not Interested', 'Considering', 'Researching']
        
        self.favourite_brands = [
            'Apple', 'Samsung', 'Nike', 'Adidas', 'Tesla', 'BMW', 'Mercedes', 'Starbucks', 
            'Whole Foods', 'Lululemon', 'Patagonia', 'North Face', 'Sony', 'Bose', 
            'Coach', 'Gucci', 'Louis Vuitton', 'Amazon', 'Netflix', 'Spotify',
            'REI', 'Target', 'Costco', 'Trader Joes', 'Peloton', 'Fitbit', 'Garmin'
        ]
        
        self.favourite_destinations = [
            'Paris', 'Tokyo', 'New York', 'London', 'Dubai', 'Barcelona', 'Rome', 
            'Sydney', 'Bali', 'Maldives', 'Iceland', 'Switzerland', 'Hawaii', 
            'Thailand', 'Greece', 'Portugal', 'Amsterdam', 'Singapore', 'Hong Kong',
            'Los Angeles', 'Miami', 'San Francisco', 'Seattle', 'Austin', 'Denver'
        ]
        
        self.hobbies = [
            'Reading', 'Painting', 'Photography', 'Hiking', 'Cycling', 'Running',
            'Yoga', 'Meditation', 'Cooking', 'Baking', 'Gardening', 'Gaming',
            'Playing Guitar', 'Piano', 'Singing', 'Dancing', 'Swimming', 'Surfing',
            'Rock Climbing', 'Camping', 'Travel Blogging', 'Vlogging', 'Podcasting',
            'Coding', 'Writing', 'Drawing', 'Sculpting', 'Pottery', 'Wine Tasting',
            'Coffee Roasting', 'Knitting', 'Woodworking', 'Car Restoration'
        ]
        
        self.imminent_events = [
            "Watch Soccer match final with friends today",
            "Surprise girlfriend with a birthday gift tomorrow",
            "Waiting anxiously for Samsung mobile phone product launch next week",
            "Planning surprise anniversary dinner for spouse this weekend",
            "Attending product demo at Apple Store tomorrow afternoon",
            "Going on first date at Italian restaurant tonight",
            "Job interview scheduled for Monday morning",
            "Marathon training run this Saturday at 6 AM",
            "Virtual yoga class starting in 2 hours",
            "Picking up new Tesla Model 3 from showroom today",
            "Concert tickets for favorite band next Friday",
            "Weekend getaway to wine country next month",
            "Dental appointment scheduled for Thursday",
            "Meeting personal trainer for first session tomorrow",
            "Attending friend's wedding ceremony this weekend",
            "Flight to Hawaii departing in 3 days",
            "Starting new diet plan from Monday",
            "House closing scheduled for end of month",
            "Baby shower for sister happening this Sunday",
            "Graduation ceremony next week",
            "Moving to new apartment this weekend",
            "Starting online MBA program next semester",
            "Expecting Amazon package delivery today",
            "Scheduled car service appointment tomorrow",
            "Birthday party tonight at favorite restaurant",
            "Zoom call with family overseas in evening",
            "Gym membership renewal due next week",
            "Book club meeting at local cafe tomorrow",
            "Photography workshop this Saturday",
            "Cooking class scheduled for Tuesday evening"
        ]
    
    def generate_insights(self, individuals, events_per_individual_range=(3, 8)):
        """
        Generate synthetic insights data for individuals
        
        Args:
            individuals: List of individual records with 'id' field
            events_per_individual_range: Tuple of (min, max) events per individual
        
        Returns:
            List of insight records
        """
        insights = []
        
        # Generate current timestamp as reference
        now = datetime.now()
        
        for individual in individuals:
            individual_id = individual.get('id', individual.get('Id'))
            
            if not individual_id:
                continue
            
            # Random number of events for this individual (time series)
            num_events = random.randint(*events_per_individual_range)
            
            # Track evolving characteristics (simulate changes over time)
            current_sentiment = random.choice(self.sentiments)
            current_lifestyle = random.choice(self.lifestyle_quotients)
            current_health = random.choice(self.health_profiles)
            current_fitness = random.choice(self.fitness_milestones)
            favourite_brand = random.choice(self.favourite_brands)
            favourite_destination = random.choice(self.favourite_destinations)
            hobby = random.choice(self.hobbies)
            
            for event_idx in range(num_events):
                # Events spread over last 90 days
                days_ago = random.randint(0, 90)
                hours_offset = random.randint(0, 23)
                minutes_offset = random.randint(0, 59)
                
                event_timestamp = now - timedelta(days=days_ago, hours=hours_offset, minutes=minutes_offset)
                
                # Occasionally change characteristics (simulate evolution)
                if random.random() < 0.3:  # 30% chance of change
                    current_sentiment = random.choice(self.sentiments)
                if random.random() < 0.2:  # 20% chance of change
                    current_lifestyle = random.choice(self.lifestyle_quotients)
                if random.random() < 0.25:  # 25% chance of change
                    current_health = random.choice(self.health_profiles)
                if random.random() < 0.15:  # 15% chance of change (fitness evolves slowly)
                    current_fitness = random.choice(self.fitness_milestones)
                if random.random() < 0.1:  # 10% chance of brand change
                    favourite_brand = random.choice(self.favourite_brands)
                if random.random() < 0.1:  # 10% chance of destination change
                    favourite_destination = random.choice(self.favourite_destinations)
                
                # Purchase intent varies more frequently
                purchase_intent = random.choice(self.purchase_intents)
                
                # Imminent event (always different)
                imminent_event = random.choice(self.imminent_events)
                
                insight_record = {
                    'Individual_Id': individual_id,
                    'Event_Timestamp': event_timestamp.isoformat(),
                    'Current_Sentiment': current_sentiment,
                    'Lifestyle_Quotient': current_lifestyle,
                    'Health_Profile': current_health,
                    'Fitness_Milestone': current_fitness,
                    'Purchase_Intent': purchase_intent,
                    'Favourite_Brand': favourite_brand,
                    'Favourite_Destination': favourite_destination,
                    'Hobby': hobby,
                    'Imminent_Event': imminent_event,
                    'data_source': 'synthetic_insights'
                }
                
                insights.append(insight_record)
        
        return insights
    
    def save_insights(self, insights, filename='data/individual_insights.json'):
        """Save insights data to JSON file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(insights, f, indent=2)
        
        return filename
    
    def get_insights_summary(self, insights):
        """Generate summary statistics for insights data"""
        total_records = len(insights)
        unique_individuals = len(set(i['Individual_Id'] for i in insights))
        
        # Count by sentiment
        sentiments = {}
        for insight in insights:
            sent = insight['Current_Sentiment']
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        # Count by lifestyle
        lifestyles = {}
        for insight in insights:
            life = insight['Lifestyle_Quotient']
            lifestyles[life] = lifestyles.get(life, 0) + 1
        
        # Count by purchase intent
        intents = {}
        for insight in insights:
            intent = insight['Purchase_Intent']
            intents[intent] = intents.get(intent, 0) + 1
        
        return {
            'total_records': total_records,
            'unique_individuals': unique_individuals,
            'avg_records_per_individual': round(total_records / unique_individuals, 2) if unique_individuals > 0 else 0,
            'sentiment_distribution': sentiments,
            'lifestyle_distribution': lifestyles,
            'purchase_intent_distribution': intents
        }


