from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from datetime import datetime
import logging
import requests
import os
import re
from dotenv import load_dotenv

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
led_status = "OFF" 

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
def index():
    try:
        global led_status
        temperature = get_pico_temperature()
        logger.debug(f"Status: {led_status}, Temperature: {temperature}")
        return render_template('index.html', 
                             now=datetime.now(),
                             status=led_status,
                             temperature=temperature)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/light_on')
def light_on():
    try:
        global led_status
        response = requests.get(f"{PICO_URL}/lighton")
        if response.status_code == 200:
            led_status = "ON"
            logger.info("LED turned ON")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error turning light on: {str(e)}")
        return f"Error controlling LED: {str(e)}", 500

@app.route('/light_off')
def light_off():
    try:
        global led_status
        response = requests.get(f"{PICO_URL}/lightoff")
        if response.status_code == 200:
            led_status = "OFF"
            logger.info("LED turned OFF")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error turning light off: {str(e)}")
        return f"Error controlling LED: {str(e)}", 500

@app.route('/flash')
def flash():
    try:
        global led_status
        response = requests.get(f"{PICO_URL}/flash")
        if response.status_code == 200:
            led_status = "FLASH"
            logger.info("LED set to FLASH")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error flashing LED: {str(e)}")
        return f"Error controlling LED: {str(e)}", 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                             'favicon.ico', mimetype='image/x-icon')

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5001)