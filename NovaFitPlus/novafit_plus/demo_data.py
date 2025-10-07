"""
Demo Data Generator for NovaFit Plus
===================================
Automatically generates realistic fake data for demonstration purposes using Faker.
Creates convincing user profiles, activities, water intake, and weather data.
"""

import random
import datetime as dt
from typing import List, Dict, Any, Optional
from faker import Faker
from .db import (
    upsert_user, upsert_activity, add_water_intake, 
    insert_weather, get_user, daily_water_total
)

fake = Faker()

class DemoDataGenerator:
    """
    Advanced demo data generator that creates realistic, coherent demo data
    for NovaFit Plus health tracking application.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.demo_users = []
        self.weather_locations = [
            {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lon": -3.7038},
            {"city": "Barcelona", "country": "Spain", "lat": 41.3851, "lon": 2.1734},
            {"city": "Valencia", "country": "Spain", "lat": 39.4699, "lon": -0.3763},
            {"city": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060},
            {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
            {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
        ]
        self.weather_conditions = [
            "Sunny", "Partly Cloudy", "Cloudy", "Light Rain", 
            "Rain", "Thunderstorm", "Snow", "Foggy", "Windy"
        ]
    
    def generate_realistic_user(self) -> Dict[str, Any]:
        """Generate a realistic user profile with coherent data"""
        age = random.randint(18, 75)
        sex = random.choice(["M", "F"])
        
        # Realistic height and weight based on demographics
        if sex == "M":
            height = random.normalvariate(175, 10)  # cm
            bmi = random.normalvariate(24, 3)  # Normal BMI range
        else:
            height = random.normalvariate(162, 8)   # cm
            bmi = random.normalvariate(23, 3)  # Normal BMI range
        
        height = max(150, min(200, height))  # Clamp realistic range
        bmi = max(18, min(35, bmi))  # Clamp realistic BMI
        weight = bmi * (height/100) ** 2
        
        location = random.choice(self.weather_locations)
        
        user_data = {
            "name": fake.name(),
            "age": age,
            "sex": sex,
            "height": round(height, 1),
            "weight": round(weight, 1),
            "activity_level": random.choice(["sedentary", "light", "moderate", "active", "very_active"]),
            "city": location["city"],
            "country": location["country"]
        }
        
        return user_data
    
    def generate_realistic_activity(self, user_data: Dict, date: dt.date) -> Dict[str, Any]:
        """Generate realistic daily activity based on user profile and consistency"""
        base_steps = {
            "sedentary": (2000, 5000),
            "light": (4000, 8000),
            "moderate": (6000, 12000),
            "active": (8000, 15000),
            "very_active": (10000, 20000)
        }
        
        activity_level = user_data["activity_level"]
        min_steps, max_steps = base_steps.get(activity_level, (5000, 10000))
        
        # Add weekly patterns (less active on weekends for some people)
        if date.weekday() >= 5 and random.random() < 0.3:  # Weekend
            steps = random.randint(int(min_steps * 0.7), int(max_steps * 0.8))
        else:
            steps = random.randint(min_steps, max_steps)
        
        # Calories roughly based on steps and weight
        calories_per_step = 0.04 + (user_data["weight"] / 1000)
        calories = int(steps * calories_per_step) + random.randint(-50, 100)
        
        # Sleep patterns
        age = user_data["age"]
        if age < 25:
            sleep_hours = random.normalvariate(8.5, 1.2)
        elif age < 50:
            sleep_hours = random.normalvariate(7.5, 1.0)
        else:
            sleep_hours = random.normalvariate(7.0, 1.1)
        
        sleep_hours = max(4.0, min(12.0, sleep_hours))
        
        # Mood based on activity and sleep
        mood = 3  # Neutral base
        if steps > max_steps * 0.8:
            mood += random.choice([0, 1])
        if sleep_hours >= 7.5:
            mood += random.choice([0, 1])
        if sleep_hours < 6:
            mood -= random.choice([0, 1])
        
        mood = max(1, min(5, mood))
        
        # Generate contextual notes
        notes = self._generate_activity_notes(steps, sleep_hours, mood, date.weekday())
        
        return {
            "steps": steps,
            "calories": calories,
            "sleep_hours": round(sleep_hours, 1),
            "mood": mood,
            "notes": notes
        }
    
    def _generate_activity_notes(self, steps: int, sleep: float, mood: int, weekday: int) -> str:
        """Generate contextual activity notes"""
        notes = []
        
        if steps > 12000:
            notes.append(random.choice([
                "Great workout day! 💪", "Long walk in the park",
                "Hiking adventure", "Active day at work",
                "Dance class was amazing", "Cycling to work"
            ]))
        elif steps < 3000:
            notes.append(random.choice([
                "Rest day", "Working from home", "Rainy day indoors",
                "Feeling under the weather", "Desk work all day"
            ]))
        
        if sleep < 6:
            notes.append(random.choice([
                "Poor sleep", "Insomnia", "Late night work",
                "Baby kept me up", "Stress"
            ]))
        elif sleep > 9:
            notes.append(random.choice([
                "Great sleep!", "Weekend lie-in", "Caught up on rest",
                "Perfect 8 hours", "Refreshing sleep"
            ]))
        
        if mood == 5:
            notes.append(random.choice([
                "Feeling fantastic! 😊", "Great mood today",
                "Everything going well", "Productive day"
            ]))
        elif mood == 1:
            notes.append(random.choice([
                "Rough day", "Feeling stressed", "Need motivation",
                "Challenging day"
            ]))
        
        # Weekend/weekday specific notes
        if weekday >= 5:  # Weekend
            notes.append(random.choice([
                "Weekend vibes", "Family time", "Relaxing weekend",
                "Social activities", "Outdoor adventures"
            ]))
        
        return " | ".join(notes[:2]) if notes else "Regular day"
    
    def generate_water_intake_pattern(self, user_data: Dict, date: dt.date) -> List[int]:
        """Generate realistic water intake pattern throughout the day"""
        target_ml = 2000 + (user_data["weight"] - 70) * 20  # Adjust for weight
        
        # Seasonal adjustments
        month = date.month
        if month in [6, 7, 8]:  # Summer
            target_ml *= 1.2
        elif month in [12, 1, 2]:  # Winter
            target_ml *= 0.9
        
        # Generate drinking sessions throughout the day
        sessions = []
        remaining_ml = target_ml
        
        # Morning (6-10 AM)
        morning_amount = random.randint(200, 500)
        sessions.append(morning_amount)
        remaining_ml -= morning_amount
        
        # Throughout the day (10 AM - 8 PM)
        num_sessions = random.randint(4, 8)
        for _ in range(num_sessions):
            if remaining_ml <= 0:
                break
            amount = min(remaining_ml, random.randint(150, 400))
            sessions.append(amount)
            remaining_ml -= amount
        
        # Evening if needed
        if remaining_ml > 100:
            sessions.append(min(remaining_ml, random.randint(100, 300)))
        
        return sessions
    
    def generate_weather_data(self, location: Dict, date: dt.date) -> Dict[str, Any]:
        """Generate realistic weather data for a location and date"""
        # Seasonal temperature patterns
        month = date.month
        base_temp = {
            1: 5, 2: 8, 3: 12, 4: 16, 5: 21, 6: 26,
            7: 29, 8: 28, 9: 24, 10: 18, 11: 12, 12: 7
        }.get(month, 15)
        
        # Add location-based adjustments
        if "Spain" in location["country"]:
            base_temp += 5
        elif "UK" in location["country"]:
            base_temp -= 3
        elif "Japan" in location["country"]:
            base_temp += 2
        
        temp_max = base_temp + random.randint(-5, 8)
        temp_min = temp_max - random.randint(3, 12)
        
        humidity = random.randint(30, 90)
        wind_speed = random.randint(5, 25)
        condition = random.choice(self.weather_conditions)
        
        return {
            "temp_max": temp_max,
            "temp_min": temp_min,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "condition": condition
        }
    
    def populate_demo_user(self, user_name: str, days_back: int = 30) -> str:
        """
        Populate a demo user with realistic data for the specified number of days
        Returns the user name that was created
        """
        # Generate user profile
        user_data = self.generate_realistic_user()
        user_data["name"] = user_name  # Use provided name
        
        # Create user in database
        upsert_user(
            self.db_path,
            user_data["name"],
            user_data["age"],
            user_data["sex"],
            user_data["height"],
            user_data["weight"],
            user_data["activity_level"],
            user_data["city"],
            user_data["country"]
        )
        
        # Generate historical data
        end_date = dt.date.today()
        
        for i in range(days_back):
            current_date = end_date - dt.timedelta(days=i)
            date_str = current_date.isoformat()
            
            # Generate activity data
            activity = self.generate_realistic_activity(user_data, current_date)
            upsert_activity(
                self.db_path,
                user_name,
                date_str,
                activity["steps"],
                activity["calories"],
                activity["mood"],
                activity["notes"],
                activity["sleep_hours"]
            )
            
            # Generate water intake
            water_sessions = self.generate_water_intake_pattern(user_data, current_date)
            for amount in water_sessions:
                add_water_intake(self.db_path, user_name, date_str, amount, "demo_data")
            
            # Generate weather data (every few days to avoid clutter)
            if i % 3 == 0:
                location = next(
                    loc for loc in self.weather_locations 
                    if loc["city"] == user_data["city"]
                )
                weather = self.generate_weather_data(location, current_date)
                insert_weather(
                    self.db_path,
                    date_str,
                    user_data["city"],
                    location["lat"],
                    location["lon"],
                    weather["temp_max"],
                    weather["temp_min"],
                    weather["humidity"],
                    weather["wind_speed"],
                    weather["condition"]
                )
        
        self.demo_users.append(user_data)
        return user_name
    
    def create_demo_dataset(self, num_users: int = 3, days_back: int = 30) -> List[str]:
        """
        Create a complete demo dataset with multiple users
        Returns list of created user names
        """
        demo_user_names = []
        
        for i in range(num_users):
            user_name = f"Demo User {i+1}"
            created_name = self.populate_demo_user(user_name, days_back)
            demo_user_names.append(created_name)
        
        return demo_user_names
    
    def quick_demo_setup(self) -> str:
        """
        Quick setup for immediate demo - creates one user with 14 days of data
        Returns the demo user name
        """
        demo_name = "Alex Demo"
        return self.populate_demo_user(demo_name, days_back=14)


def populate_demo_data(db_path: str, user_name: str = "Demo User", days: int = 14) -> str:
    """
    Convenience function to quickly populate demo data
    """
    generator = DemoDataGenerator(db_path)
    return generator.populate_demo_user(user_name, days)


def create_full_demo(db_path: str) -> List[str]:
    """
    Create a full demo dataset with multiple users and comprehensive data
    """
    generator = DemoDataGenerator(db_path)
    return generator.create_demo_dataset(num_users=3, days_back=30)