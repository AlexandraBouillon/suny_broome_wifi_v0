from flask import Flask, render_template, redirect, url_for, send_from_directory, jsonify, request
from datetime import datetime
import requests
import re
import urllib3
import openai
from config import Config, logger
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get PICO_URL from environment
PICO_URL = os.environ.get('NGROK_URL')

# Initialize Flask
app = Flask(__name__, 
           template_folder=Config.TEMPLATE_DIR,
           static_folder=Config.STATIC_DIR)

# Global variables
led_status = "OFF"

# Helper functions
def make_request(url, description="Request"):
    """Make a request to the Pico with standard headers and logging"""
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
        'ngrok-skip-browser-warning': 'true'
    }
    
    logger.info("=" * 50)
    logger.info(f"{description}")
    logger.info(f"Sending request to: {url}")
    
    response = requests.get(url, 
                          headers=headers,
                          verify=False, 
                          timeout=10)
    
    logger.info(f"Response Status: {response.status_code}")
    return response

def parse_pico_response(response):
    """Parse temperature and LED state from Pico response"""
    temp_match = re.search(r'Temperature: ([\d.]+)°C', response.text)
    state_match = re.search(r'LED Status: (ON|OFF|FLASH)', response.text)
    
    temperature = float(temp_match.group(1)) if temp_match else 25.0
    if temp_match:
        logger.info(f"Found temperature: {temperature}")
    else:
        logger.error("Could not find temperature in response")
        
    if state_match:
        global led_status
        led_status = state_match.group(1)
        logger.info(f"Found LED state: {led_status}")
    else:
        logger.error("Could not find LED state in response")
        
    return temperature, led_status

def get_ai_response(user_input, context=""):
    """Get a response from OpenAI for TJ"""
    try:
        if not Config.OPENAI_API_KEY:
            return "Error: OpenAI API key not configured"
            
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
        response = completion.choices[0].message['content']
        logger.info(f"AI Response generated successfully for input: {user_input[:50]}...")
        return response
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return f"Error: {str(e)}"

def save_conversation(user_input, ai_response):
    """Save conversation history to a file"""
    try:
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response
        }
        with open('conversation_history.json', 'a') as f:
            json.dump(conversation, f)
            f.write('\n')
        logger.info("Conversation saved successfully")
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")

# Routes
@app.route('/')
def index():
    try:
        response = make_request(PICO_URL, "INDEX REQUEST")
        temperature, _ = parse_pico_response(response)
        return render_template('index.html', 
                             now=datetime.now(),
                             status=led_status,
                             temperature=temperature)
    except Exception as e:
        logger.error(f"Error in index: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not Config.CHAT_ENABLED:
            return jsonify({
                'reply': "Sorry, chat is currently disabled. Please configure the OpenAI API key to enable chat features."
            }), 503
            
        data = request.get_json()
        user_input = data.get('text', '')
        
        logger.info(f"Chat request received: {user_input[:50]}...")
        
        # Get AI response
        response = get_ai_response(user_input)
        
        return jsonify({'reply': response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/lighton')
@app.route('/light_on')
def light_on():
    try:
        urls = [f"{PICO_URL}/lighton", f"{PICO_URL}/light_on"]
        for url in urls:
            try:
                response = make_request(url, "LIGHT ON REQUEST")
                if response.status_code == 200:
                    global led_status
                    led_status = 'ON'
                    logger.info("LED turned ON successfully")
                    break
            except Exception as e:
                logger.error(f"Failed with URL {url}: {str(e)}")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in light_on: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/lightoff')
@app.route('/light_off')
def light_off():
    try:
        response = make_request(f"{PICO_URL}/light_off", "LIGHT OFF REQUEST")
        if response.status_code == 200:
            global led_status
            led_status = 'OFF'
            logger.info("LED turned OFF successfully")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in light_off: {type(e).__name__}: {str(e)}")
        return str(e), 500

@app.route('/flash')
@app.route('/flash?')
def flash():
    try:
        response = make_request(f"{PICO_URL}/flash?", "FLASH REQUEST")
        if response.status_code == 200:
            global led_status
            led_status = 'OFF'
            logger.info("Flash sequence completed")
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
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5001)