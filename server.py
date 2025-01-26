from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
import machine
import time
from config import get_ai_response, save_conversation
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global state
led_status = "OFF"  # Track LED status globally

# Setup LED and temperature sensor
try:
    led = machine.Pin("LED", machine.Pin.OUT)
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    logger.info("Hardware initialized successfully")
except Exception as e:
    logger.error(f"Error initializing hardware: {e}")
    # Create dummy objects for testing
    class DummyPin:
        def __init__(self):
            self._value = 0
        def value(self, val=None):
            if val is not None:
                self._value = val
            return self._value
    led = DummyPin()
    logger.info("Using dummy hardware for testing")

def read_temperature():
    """Read temperature from the Pico's internal temperature sensor"""
    try:
        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706) / 0.001721
        return round(temperature, 1)
    except Exception as e:
        logger.error(f"Error reading temperature: {e}")
        return 25.0  # Return dummy value for testing

def flash_led():
    """Set LED to flash mode"""
    global led_status
    try:
        led_status = "FLASH"  # Set status to FLASH
        led.value(1)  # Turn on LED initially
        logger.info("LED flash mode activated")
    except Exception as e:
        logger.error(f"Error setting flash mode: {e}")

@app.route('/')
def index():
    """Render the main page with current LED and temperature status"""
    try:
        temperature = read_temperature()
        global led_status
        return render_template('index.html', 
                             temperature=temperature, 
                             status=led_status,
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return "Error loading page", 500

@app.route('/light_on')
def light_on():
    """Turn the LED on"""
    try:
        global led_status
        led.value(1)
        led_status = "ON"
        logger.info("LED turned ON")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error turning LED on: {e}")
        return "Error controlling LED", 500

@app.route('/light_off')
def light_off():
    """Turn the LED off"""
    try:
        global led_status
        led.value(0)
        led_status = "OFF"
        logger.info("LED turned OFF")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error turning LED off: {e}")
        return "Error controlling LED", 500

@app.route('/flash')
def flash():
    """Set LED to flash mode"""
    try:
        flash_led()
        logger.info("LED flash mode initiated")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in flash sequence: {e}")
        return "Error flashing LED", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat API requests
    Returns JSON response with AI assistant's reply
    """
    try:
        # Get the user's message
        user_input = request.json.get('text', '')
        if not user_input:
            return jsonify({
                'status': 'error',
                'reply': 'Please provide a message'
            }), 400
        
        # Get current LED and temperature status for context
        temperature = read_temperature()
        context = f"LED is currently {led_status}. Temperature is {temperature}°C."
        
        # Get AI response
        ai_response = get_ai_response(user_input, context)
        
        # Save the conversation
        save_conversation(user_input, ai_response)
        
        logger.info(f"Chat request processed successfully for input: {user_input[:50]}...")
        return jsonify({
            'status': 'success',
            'reply': ai_response
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'reply': 'Sorry, I encountered an error. Please try again.'
        }), 500

@app.route('/api/status')
def get_status():
    """
    API endpoint to get current LED and temperature status
    """
    try:
        global led_status
        return jsonify({
            'status': 'success',
            'led_status': led_status,
            'temperature': read_temperature()
        })
    except Exception as e:
        logger.error(f"Status API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error getting status'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)