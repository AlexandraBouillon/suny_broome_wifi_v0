from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
from models import db, TemperatureReading, LightEvent
from config import Config, logger
from sqlalchemy import func
from dotenv import load_dotenv
import os
from random import uniform
import time
import random

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///led_control.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Add this at the top with your other imports
last_temp_update = datetime.now()

@app.route('/')
def home():
    try:
        # Get the most recent temperature reading
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        
        # Get the current light status
        latest_light_event = LightEvent.query.order_by(
            LightEvent.timestamp.desc()
        ).first()
        
        status = latest_light_event.status if latest_light_event else "OFF"
        temperature = latest_temp.temperature if latest_temp else 20.000
        
        return render_template('index.html', 
                             status=status,
                             temperature=f"{temperature:.3f}",
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return render_template('index.html', 
                             status="ERROR",
                             temperature="0.000",
                             now=datetime.now())

@app.route('/get_current_temp')
def get_current_temp():
    try:
        global last_temp_update
        
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        latest_light_event = LightEvent.query.order_by(
            LightEvent.timestamp.desc()
        ).first()
        
        current_temp = latest_temp.temperature if latest_temp else 22.718
        status = latest_light_event.status if latest_light_event else "OFF"
        
        # Calculate time since last temperature update
        now = datetime.now()
        time_since_update = (now - last_temp_update).total_seconds()
        
        # Only update if 5 or more seconds have passed since last update
        if time_since_update >= 5:
            timestamp_ms = int(time.time() * 1000)
            random_variation = (timestamp_ms % 10) * 0.0001
            
            if status == "FLASH":
                # During flash, temperature should increase
                new_temp = round(current_temp + 0.003 + random_variation, 3)
                logger.info(f"Flash active: Increasing temperature from {current_temp:.3f} to {new_temp:.3f} (variation: {random_variation:.4f})")
            elif status == "OFF" and latest_light_event and latest_light_event.status == "FLASH":
                # After flash completed (in OFF state), temperature should decrease
                new_temp = round(current_temp - 0.003 + random_variation, 3)
                logger.info(f"Post-flash cooling: Decreasing temperature from {current_temp:.3f} to {new_temp:.3f} (variation: {random_variation:.4f})")
            elif status == "ON":
                # Normal ON state
                new_temp = round(current_temp + 0.003 + random_variation, 3)
                logger.info(f"LED ON: Increasing temperature from {current_temp:.3f} to {new_temp:.3f} (variation: {random_variation:.4f})")
            else:
                # Normal OFF state
                new_temp = round(current_temp - 0.003 + random_variation, 3)
                logger.info(f"LED OFF: Decreasing temperature from {current_temp:.3f} to {new_temp:.3f} (variation: {random_variation:.4f})")
            
            # Create new temperature reading
            temp_reading = TemperatureReading(temperature=new_temp)
            db.session.add(temp_reading)
            db.session.commit()
            
            # Update the last update time
            last_temp_update = now
            
            return jsonify({
                "temperature": f"{new_temp:.3f}",
                "status": status,
                "updated": True,
                "variation": f"{random_variation:.4f}"
            })
        
        return jsonify({
            "temperature": f"{current_temp:.3f}",
            "status": status,
            "updated": False
        })
    except Exception as e:
        logger.error(f"Error getting current temperature: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/light_on')
def light_on():
    try:
        global last_temp_update
        
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        
        current_temp = latest_temp.temperature if latest_temp else 22.718
        
        # Add small random variation on state change
        timestamp_ms = int(time.time() * 1000)
        random_variation = (timestamp_ms % 10) * 0.0001
        new_temp = round(current_temp + random_variation, 3)
        
        # Create new light event
        event = LightEvent(
            status="ON",
            temperature=new_temp
        )
        
        # Create new temperature reading
        temp_reading = TemperatureReading(temperature=new_temp)
        
        db.session.add(event)
        db.session.add(temp_reading)
        db.session.commit()
        
        # Reset the temperature update timer
        last_temp_update = datetime.now()
        
        logger.info(f"Light turned ON, temperature at {new_temp:.3f}°C (variation: {random_variation:.4f})")
        return jsonify({"status": "ON", "temperature": f"{new_temp:.3f}", "success": True})
    except Exception as e:
        logger.error(f"Error turning light on: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/light_off')
def light_off():
    try:
        global last_temp_update
        
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        
        current_temp = latest_temp.temperature if latest_temp else 22.718
        
        # Add small random variation on state change
        timestamp_ms = int(time.time() * 1000)
        random_variation = (timestamp_ms % 10) * 0.0001
        new_temp = round(current_temp + random_variation, 3)
        
        # Create new light event
        event = LightEvent(
            status="OFF",
            temperature=new_temp
        )
        
        # Create new temperature reading
        temp_reading = TemperatureReading(temperature=new_temp)
        
        db.session.add(event)
        db.session.add(temp_reading)
        db.session.commit()
        
        # Reset the temperature update timer
        last_temp_update = datetime.now()
        
        logger.info(f"Light turned OFF, temperature at {new_temp:.3f}°C (variation: {random_variation:.4f})")
        return jsonify({"status": "OFF", "temperature": f"{new_temp:.3f}", "success": True})
    except Exception as e:
        logger.error(f"Error turning light off: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/flash')
def flash():
    try:
        global last_temp_update
        
        # Get current temperature
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        current_temp = latest_temp.temperature if latest_temp else 22.718
        
        # Calculate temperature increase for flash
        flash_temp = round(current_temp + 0.05, 3)  # Significant increase during flash
        
        # Store flash temperature reading
        flash_reading = TemperatureReading(
            temperature=flash_temp,
            timestamp=datetime.now()
        )
        db.session.add(flash_reading)
        
        # Calculate gradual increase over 10 seconds
        for i in range(1, 11):  # 10 readings over 10 seconds
            incremental_temp = round(flash_temp + (0.01 * i), 3)  # Continue increasing
            reading = TemperatureReading(
                temperature=incremental_temp,
                timestamp=datetime.now() + timedelta(seconds=i)
            )
            db.session.add(reading)
        
        db.session.commit()
        last_temp_update = datetime.now()
        
        logger.info(
            f"Flash executed: Initial temp {current_temp:.3f} → Peak {flash_temp:.3f} "
            f"→ Final {incremental_temp:.3f}"
        )
        
        return jsonify({
            "status": "FLASH",
            "initial_temp": f"{current_temp:.3f}",
            "flash_temp": f"{flash_temp:.3f}",
            "final_temp": f"{incremental_temp:.3f}",
            "success": True
        })
    except Exception as e:
        logger.error(f"Error executing flash: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_temperature')
def update_temperature():
    try:
        global last_temp_update
        
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        current_temp = latest_temp.temperature if latest_temp else 22.718
        
        status = request.args.get('status', 'OFF')
        random_variation = random.uniform(-0.001, 0.001)
        
        if status == "ON":
            # Normal ON state
            new_temp = round(current_temp + 0.003 + random_variation, 3)
            logger.info(f"LED ON: Increasing temperature from {current_temp:.3f} to {new_temp:.3f} (variation: {random_variation:.4f})")
        elif status == "FLASH":
            # Flash state - higher increase
            new_temp = round(current_temp + 0.005 + abs(random_variation), 3)
            logger.info(f"LED FLASH: Increasing temperature from {current_temp:.3f} to {new_temp:.3f}")
        else:
            # OFF state
            new_temp = round(current_temp - 0.002 + random_variation, 3)
            logger.info(f"LED OFF: Decreasing temperature from {current_temp:.3f} to {new_temp:.3f} (variation: {random_variation:.4f})")
        
        reading = TemperatureReading(
            temperature=new_temp,
            timestamp=datetime.now()
        )
        db.session.add(reading)
        db.session.commit()
        
        last_temp_update = datetime.now()
        
        return jsonify({
            "temperature": f"{new_temp:.3f}",
            "previous_temperature": f"{current_temp:.3f}",
            "success": True
        })
    except Exception as e:
        logger.error(f"Error updating temperature: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('text', '').lower()
        logger.info(f"Received chat request with input: {user_input}")
        
        # Get the time range for the query (default to last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        logger.info(f"Querying between {start_date} and {end_date}")
        
        # Calculate statistics based on user query
        if "temperature" in user_input:
            logger.info("Processing temperature query")
            # Debug: Count temperature readings
            count = db.session.query(TemperatureReading).filter(
                TemperatureReading.timestamp.between(start_date, end_date)
            ).count()
            logger.info(f"Found {count} temperature readings in the date range")
            
            avg_temp = db.session.query(func.avg(TemperatureReading.temperature)).filter(
                TemperatureReading.timestamp.between(start_date, end_date)
            ).scalar()
            
            if avg_temp is None:
                logger.warning("No temperature readings found in the specified time range")
                response = "I couldn't find any temperature readings for the past week."
            else:
                logger.info(f"Retrieved average temperature: {avg_temp:.2f}°C")
                response = f"The average temperature over the past week has been {avg_temp:.2f}°C"
        elif "light" in user_input or "on time" in user_input:
            total_hours = LightEvent.get_total_on_time(start_date, end_date)
            response = f"The light has been on for {total_hours:.2f} hours over the past week"
        else:
            logger.info(f"No temperature keyword found in: {user_input}")
            response = "I can tell you about temperature readings and light usage. Just ask!"
            
        logger.info(f"Sending response: {response}")
        return jsonify({'reply': response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_temp')
def get_temp():
    try:
        # Get current temperature and light status
        latest_temp = TemperatureReading.query.order_by(
            TemperatureReading.timestamp.desc()
        ).first()
        
        latest_light = LightEvent.query.order_by(
            LightEvent.timestamp.desc()
        ).first()
        
        current_temp = latest_temp.temperature if latest_temp else 20.000
        light_status = latest_light.status if latest_light else "OFF"
        
        # If light has been in current state for more than 3 seconds, adjust temperature
        if latest_light and (datetime.now() - latest_light.timestamp).total_seconds() > 3:
            if light_status == "ON":
                new_temp = round(current_temp + 0.010 + uniform(0.001, 0.009), 3)
            else:
                new_temp = round(current_temp - 0.010 + uniform(-0.009, -0.001), 3)
                
            # Record new temperature
            temp_reading = TemperatureReading(temperature=new_temp)
            db.session.add(temp_reading)
            db.session.commit()
            
            return jsonify({"temperature": f"{new_temp:.3f}", "status": light_status})
            
        return jsonify({"temperature": f"{current_temp:.3f}", "status": light_status})
    except Exception as e:
        logger.error(f"Error getting temperature: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)