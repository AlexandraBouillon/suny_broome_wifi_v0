from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from datetime import datetime
import logging
import requests
import os
import re
import urllib3

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

logger.info(f"Current directory: {current_dir}")
logger.info(f"Template directory: {template_dir}")
logger.info(f"Static directory: {static_dir}")

# Verify the directories exist
if not os.path.exists(template_dir):
    raise FileNotFoundError(f"Template directory not found at: {template_dir}")
if not os.path.exists(static_dir):
    raise FileNotFoundError(f"Static directory not found at: {static_dir}")

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# Get the PICO_URL from environment variable
PICO_URL = os.environ.get('PICO_URL', 'https://d5b3-2603-7081-5500-76ad-b5b0-27bf-e53c-aa5e.ngrok-free.app')
NGROK_URL = os.getenv('NGROK_URL')
led_status = "OFF" 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

def get_pico_temperature():
    try:
        logger.info("=" * 50)
        logger.info("TEMPERATURE REQUEST")
        logger.info(f"PICO_URL: {PICO_URL}")
        
       
        urls_to_try = [
            PICO_URL,
            f"{PICO_URL}/",
            f"{PICO_URL}/flash"  
        ]
        
        for url in urls_to_try:
            try:
                logger.info(f"Trying URL: {url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'text/html,application/json',
                    'Connection': 'keep-alive'
                }
                
                response = requests.get(url, 
                                      headers=headers,
                                      verify=False, 
                                      timeout=10)
                
                logger.info(f"Response Status: {response.status_code}")
                logger.info(f"Response Headers: {dict(response.headers)}")
                logger.info(f"Response Content Preview: {response.text[:200]}")
                
             
                temp_match = re.search(r'<div class="temperature">Temperature: ([\d.]+)°C</div>', response.text)
                if temp_match:
                    temp = float(temp_match.group(1))
                    logger.info(f"Found temperature: {temp}°C")
                    return temp
                
            except Exception as e:
                logger.error(f"Error with URL {url}: {type(e).__name__}: {str(e)}")
                continue
        
        logger.error("Temperature not found in any response")
        return 25.0
        
    except Exception as e:
        logger.error(f"Unexpected error in get_pico_temperature: {type(e).__name__}: {str(e)}")
        return 25.0

@app.route('/')
def index():
    try:
        global led_status
        logger.info("=" * 50)
        logger.info("INDEX REQUEST")
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'ngrok-skip-browser-warning': 'true'
        }
        
    
        response = requests.get(PICO_URL, 
                              headers=headers,
                              verify=False, 
                              timeout=10)
        
        logger.info(f"Response Status: {response.status_code}")
        
        temp_match = re.search(r'Temperature: ([\d.]+)°C', response.text)
        if temp_match:
            temperature = float(temp_match.group(1))
            logger.info(f"Found temperature: {temperature}")
        else:
            temperature = 25.0
            logger.error("Could not find temperature in response")
            
   
        state_match = re.search(r'LED Status: (ON|OFF|FLASH)', response.text)
        if state_match:
            led_status = state_match.group(1)
            logger.info(f"Found LED state: {led_status}")
        else:
            logger.error("Could not find LED state in response")
                
        return render_template('index.html', 
                             now=datetime.now(),
                             status=led_status,
                             temperature=temperature)
    except Exception as e:
        logger.error(f"Error in index: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/lighton')
@app.route('/light_on')
def light_on():
    try:
        global led_status
        # Try both URL patterns
        urls_to_try = [
            f"{PICO_URL}/lighton",
            f"{PICO_URL}/lighton?",
            f"{PICO_URL}/light_on",
        ]
        
        logger.info("=" * 50)
        logger.info("LIGHT ON REQUEST")
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'ngrok-skip-browser-warning': 'true'
        }
        
        success = False
        for url in urls_to_try:
            try:
                logger.info(f"Trying URL: {url}")
                response = requests.get(url, 
                                     headers=headers,
                                     verify=False, 
                                     timeout=10)
                
                logger.info(f"Response Status: {response.status_code}")
                logger.info(f"Response Content: {response.text[:200]}")
                
                if response.status_code == 200:
                    led_status = 'ON'
                    logger.info("LED turned ON successfully")
                    success = True
                    break
            except Exception as e:
                logger.error(f"Failed with URL {url}: {str(e)}")
                continue
        
        if not success:
            logger.error("All URL attempts failed")
            
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/lightoff')
@app.route('/light_off')
def light_off():
    try:
        global led_status
        url = f"{PICO_URL}/light_off" 
        
        logger.info("=" * 50)
        logger.info("LIGHT OFF REQUEST")
        logger.info(f"Sending request to: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'ngrok-skip-browser-warning': 'true'
        }
        
        response = requests.get(url, 
                              headers=headers,
                              verify=False, 
                              timeout=10)
        
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            led_status = 'OFF'
            logger.info("LED turned OFF successfully")
        else:
            logger.error(f"Failed to turn LED OFF. Status: {response.status_code}")
            
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in light_off: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/flash')
@app.route('/flash?')
def flash():
    try:
        global led_status
        url = f"{PICO_URL}/flash?"
        logger.info("=" * 50)
        logger.info("FLASH REQUEST")
        logger.info(f"Sending request to: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'ngrok-skip-browser-warning': 'true'
        }
        
        response = requests.get(url, 
                              headers=headers,
                              verify=False, 
                              timeout=10)
        
        logger.info(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            led_status = 'OFF'  # Flash sets state to OFF in Pico code
            logger.info("Flash sequence completed")
        else:
            logger.error(f"Failed to flash LED. Status: {response.status_code}")
            
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in flash: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                             'favicon.ico', mimetype='image/x-icon')

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5001)