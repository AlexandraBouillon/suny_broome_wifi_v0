from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class TemperatureReading(db.Model):
    __tablename__ = 'temperature_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class LightEvent(db.Model):
    __tablename__ = 'light_events'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(10), nullable=False)  # 'ON' or 'OFF'
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def get_total_on_time(cls, start_date, end_date):
        """Calculate total time light was on between two dates"""
        events = cls.query.filter(
            cls.timestamp.between(start_date, end_date)
        ).order_by(cls.timestamp).all()
        
        total_seconds = 0
        last_on = None
        
        for event in events:
            if event.status == 'ON':
                last_on = event.timestamp
            elif event.status == 'OFF' and last_on:
                total_seconds += (event.timestamp - last_on).total_seconds()
                last_on = None
                
        # Handle case where light is still on
        if last_on:
            total_seconds += (datetime.utcnow() - last_on).total_seconds()
            
        return total_seconds / 3600  # Convert to hours 