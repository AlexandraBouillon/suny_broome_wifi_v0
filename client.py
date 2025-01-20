from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import requests
import logging
import sys
from config import NGROK_URL
import urllib3
import re

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/SUNYBROOMEPROJECT/suny_broome_wifi_v0/debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings()

# Initialize Flask with static folder
app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    status = "Unknown"
    temperature = "Unknown"
    try:
        # Get full response which includes both status and temperature
        response = requests.get(f"{NGROK_URL}/", verify=False, timeout=5)
        html_text = response.text
        
        # Parse LED status with icon
        if "LED is ON" in html_text:
            status = "ON 💡"
        elif "LED is OFF" in html_text:
            status = "OFF ⭕"
            
        # Parse temperature with better formatting
        temp_match = re.search(r'Temperature is ([\d.]+)', html_text)
        if temp_match:
            temp = float(temp_match.group(1))
            temperature = f"{temp:.2f}"  # Format to 2 decimal places
            logger.info(f"Found temperature: {temperature}")
        else:
            logger.error(f"Temperature not found in response: {html_text}")
            
        logger.info(f"Status: {status}, Temperature: {temperature}")
    except Exception as e:
        logger.error(f"Error checking status/temperature: {str(e)}")
        status = "Error ⚠️"
        temperature = "Error ⚠️"
    return render_template('index.html', status=status, temperature=temperature)

@app.route('/light_on')
def light_on():
    try:
        full_url = f"{NGROK_URL}/lighton?"
        logger.info(f"Attempting to connect to: {full_url}")
        response = requests.get(
            full_url,
            verify=False, 
            timeout=10,
            headers={
                'User-Agent': 'PythonAnywhere-Client',
                'Accept': '*/*'
            }
        )
        logger.info(f"Full response: Status={response.status_code}, Text='{response.text}'")
        return home()
    except requests.exceptions.Timeout:
        logger.error("Request timed out while connecting to Pico")
        return "Connection timed out", 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return "Failed to connect to Pico", 502
    except Exception as e:
        logger.error(f"Unexpected error in light_on: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/light_off')
def light_off():
    try:
        full_url = f"{NGROK_URL}/lightoff?"
        logger.info(f"Attempting to connect to: {full_url}")
        response = requests.get(
            full_url,
            verify=False, 
            timeout=10,
            headers={
                'User-Agent': 'PythonAnywhere-Client',
                'Accept': '*/*'
            }
        )
        logger.info(f"Full response: Status={response.status_code}, Text='{response.text}'")
        return home()
    except requests.exceptions.Timeout:
        logger.error("Request timed out while connecting to Pico")
        return "Connection timed out", 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return "Failed to connect to Pico", 502
    except Exception as e:
        logger.error(f"Unexpected error in light_off: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/flash')
def flash():
    try:
        full_url = f"{NGROK_URL}/flash?"
        logger.info(f"Attempting to connect to: {full_url}")
        response = requests.get(
            full_url,
            verify=False, 
            timeout=10,
            headers={
                'User-Agent': 'PythonAnywhere-Client',
                'Accept': '*/*'
            }
        )
        logger.info(f"Flash response: Status={response.status_code}, Text='{response.text}'")
        return home()
    except requests.exceptions.Timeout:
        logger.error("Request timed out while connecting to Pico")
        return "Connection timed out", 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return "Failed to connect to Pico", 502
    except Exception as e:
        logger.error(f"Unexpected error in flash: {str(e)}")
        return f"Error: {str(e)}", 500

# Add route for serving static files (if needed)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)