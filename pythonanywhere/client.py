from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import requests
import logging
import sys
from datetime import datetime
from config import NGROK_URL, Secrets, get_ai_response
import urllib3
import re

# Configure logging
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

# Initialize Flask app
app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    status = "Unknown"
    temperature = "Unknown"
    try:
        # Get status and temperature from Pico
        response = requests.get(f"{NGROK_URL}/", verify=False, timeout=5)
        html_text = response.text
        
        # Parse LED status with icon
        if "LED is ON" in html_text:
            status = "ON 💡"
        elif "LED is OFF" in html_text:
            status = "OFF ⭕"
            
        # Parse temperature with formatting
        temp_match = re.search(r'Temperature is ([\d.]+)', html_text)
        if temp_match:
            temp = float(temp_match.group(1))
            temperature = f"{temp:.2f}"
            logger.info(f"Found temperature: {temperature}")
        else:
            logger.error(f"Temperature not found in response: {html_text}")
            
        logger.info(f"Status: {status}, Temperature: {temperature}")
    except Exception as e:
        logger.error(f"Error checking status/temperature: {str(e)}")
        status = "Error ⚠️"
        temperature = "Error ⚠️"
    
    return render_template('index.html', 
                         status=status, 
                         temperature=temperature,
                         now=datetime.now())

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
        logger.info(f"Light on response: Status={response.status_code}, Text='{response.text}'")
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
        logger.info(f"Light off response: Status={response.status_code}, Text='{response.text}'")
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
        # Instead of calling home(), just return a success response
        return jsonify({
            "status": "success",
            "message": "Flash command sent",
            "led_status": "FLASH"
        })
    except requests.exceptions.Timeout:
        logger.error("Request timed out while connecting to Pico")
        return "Connection timed out", 504
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return "Failed to connect to Pico", 502
    except Exception as e:
        logger.error(f"Unexpected error in flash: {str(e)}")
        return f"Error: {str(e)}", 500

# New chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('text', '')
        logger.info(f"Chat request received: {user_input}")

        # Get current status for context
        status = "Unknown"
        temperature = "Unknown"
        try:
            response = requests.get(f"{NGROK_URL}/", verify=False, timeout=5)
            html_text = response.text
            if "LED is ON" in html_text:
                status = "ON"
            elif "LED is OFF" in html_text:
                status = "OFF"
            temp_match = re.search(r'Temperature is ([\d.]+)', html_text)
            if temp_match:
                temperature = temp_match.group(1)
        except Exception as e:
            logger.error(f"Error getting status for chat context: {str(e)}")

        context = f"LED is currently {status}. Temperature is {temperature}°C."
        
        response = get_ai_response(user_input, context)
        logger.info(f"Chat response generated: {response}")
        
        return jsonify({
            "reply": response,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "reply": "Sorry, I encountered an error processing your request.",
            "status": "error",
            "error": str(e)
        }), 500

# Static file routes
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)