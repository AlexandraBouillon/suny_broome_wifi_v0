from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from datetime import datetime
import logging
import requests
import os
import re
from dotenv import load_dotenv
import openai
from config import Config, logger
from services.chat_service import get_ai_response
from services.led_service import LEDService

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))   
PROJECT_ROOT = os.path.dirname(current_dir)  


template_dir = os.path.join(PROJECT_ROOT, 'templates')
static_dir = os.path.join(PROJECT_ROOT, 'static')

logger.info(f"Current directory: {current_dir}")
logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Template directory: {template_dir}")
logger.info(f"Static directory: {static_dir}")

if not os.path.exists(template_dir):
    raise FileNotFoundError(f"Template directory not found at: {template_dir}")
if not os.path.exists(static_dir):
    raise FileNotFoundError(f"Static directory not found at: {static_dir}")

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

PICO_URL = os.getenv('PICO_URL', 'http://192.168.1.137')
NGROK_URL = os.getenv('NGROK_URL')
led_service = LEDService()

# Configure OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    CHAT_ENABLED = True
    logger.info("OpenAI API key configured")
else:
    CHAT_ENABLED = False
    logger.warning("OpenAI API key not found - Chat features will be disabled")

def get_pico_temperature():
    try:
        response = requests.get(PICO_URL)
        content = response.text
        
        temp_match = re.search(r'Temperature is ([\d.]+)', content)
        if temp_match:
            temp = float(temp_match.group(1))
            logger.debug(f"Found temperature: {temp}°C")
            return temp
        
        logger.error("Could not find temperature in response")
        return 25.0
    except Exception as e:
        logger.error(f"Error getting temperature: {e}")
        return 25.0

@app.route('/')
def home():
    try:
        status = led_service.get_status()
        temperature = led_service.get_temperature()
        logger.info(f"Home route - LED status: {status}, Temperature: {temperature}")
        return render_template('index.html', 
                             status=status,
                             temperature=temperature,
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return render_template('index.html', 
                             status="ERROR",
                             temperature=0,
                             now=datetime.now())

@app.route('/light_on')
def light_on():
    try:
        led_service.turn_on()
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error turning light on: {e}")
        return redirect(url_for('home'))

@app.route('/light_off')
def light_off():
    try:
        led_service.turn_off()
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error turning light off: {e}")
        return redirect(url_for('home'))

@app.route('/flash')
def flash():
    try:
        status = led_service.flash()
        logger.info(f"Flash status: {status}")
        # Get fresh status and temperature before redirecting
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error setting flash: {e}")
        return redirect(url_for('home'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                             'favicon.ico', mimetype='image/x-icon')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('text', '')
        logger.info(f"Chat request received: {user_input[:50]}...")
        response = get_ai_response(user_input)
        return jsonify({'reply': response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server on port 5001...")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")