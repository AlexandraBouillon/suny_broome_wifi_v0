from datetime import datetime, timedelta
import random
import math
import sys
import os

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, TemperatureReading, LightEvent
from server import app

def generate_temperature(timestamp):
    """Generate realistic temperature with seasonal and daily variations"""
    # Base temperature (yearly average)
    base_temp = 20.0
    
    # Seasonal variation (±5°C)
    day_of_year = timestamp.timetuple().tm_yday
    seasonal_variation = 5 * math.sin(2 * math.pi * (day_of_year - 81) / 365)
    
    # Daily variation (±3°C)
    hour = timestamp.hour
    daily_variation = 3 * math.sin(2 * math.pi * (hour - 4) / 24)
    
    # Random noise (±0.5°C)
    noise = random.uniform(-0.5, 0.5)
    
    temperature = base_temp + seasonal_variation + daily_variation + noise
    return round(temperature, 2)

def generate_light_events(start_date, end_date):
    """Generate random light events"""
    events = []
    current_date = start_date
    status = "OFF"
    
    while current_date < end_date:
        # More likely to turn on during evening hours
        hour = current_date.hour
        if status == "OFF" and (
            (hour >= 17 and hour <= 23 and random.random() < 0.3) or  # Evening
            (hour >= 0 and hour <= 5 and random.random() < 0.1) or    # Night
            (hour >= 6 and hour <= 16 and random.random() < 0.05)     # Day
        ):
            status = "ON"
            events.append((current_date, status))
        elif status == "ON" and random.random() < 0.2:  # 20% chance to turn off
            status = "OFF"
            events.append((current_date, status))
            
        current_date += timedelta(hours=1)
    
    return events

def main():
    # Generate one year of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    with app.app_context():
        # Clear existing data
        db.session.query(TemperatureReading).delete()
        db.session.query(LightEvent).delete()
        
        # Generate temperature readings (every hour)
        current = start_date
        while current < end_date:
            temp = generate_temperature(current)
            reading = TemperatureReading(
                temperature=temp,
                timestamp=current
            )
            db.session.add(reading)
            current += timedelta(hours=1)
        
        # Generate light events
        light_events = generate_light_events(start_date, end_date)
        for timestamp, status in light_events:
            # Get the temperature reading closest to this timestamp
            temp = generate_temperature(timestamp)
            event = LightEvent(
                status=status,
                temperature=temp,
                timestamp=timestamp
            )
            db.session.add(event)
        
        # Commit all changes
        db.session.commit()
        
        # Print summary
        temp_count = TemperatureReading.query.count()
        event_count = LightEvent.query.count()
        print(f"Generated {temp_count} temperature readings")
        print(f"Generated {event_count} light events")

if __name__ == "__main__":
    main() 