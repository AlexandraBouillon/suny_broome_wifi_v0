from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from datetime import datetime
import logging
import requests
import os
import re
from dotenv import load_dotenv
import openai

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

def get_ai_response(user_input, context=""):
    """Get a response from OpenAI for TJ"""
    try:
        if not CHAT_ENABLED:
            return "Chat is currently disabled. Please configure the OpenAI API key."

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are TJ, an assistant for a Raspberry Pi Pico W LED Control Panel. {context}"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        return completion.choices[0].message['content']
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
        return "Error: API rate limit exceeded. Please try again later."
    except openai.error.AuthenticationError:
        logger.error("OpenAI API authentication failed")
        return "Error: API authentication failed. Please check your API key."
    except openai.error.InvalidRequestError as e:
        logger.error(f"OpenAI API invalid request: {str(e)}")
        return f"Error: Invalid request - {str(e)}"
    except Exception as e:
        logger.error(f"Error getting AI response: {type(e).__name__}: {str(e)}")
        return f"Error: {str(e)}"

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
    logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5001)