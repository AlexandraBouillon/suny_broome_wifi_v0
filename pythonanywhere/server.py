from flask import Flask, render_template, jsonify, request, redirect, url_for
import openai
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from services.chat_service import get_ai_response
from services.pico_service import PicoService
from config import Config, logger

# Load environment variables
load_dotenv()

# Configure OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    CHAT_ENABLED = True
    logger.info("OpenAI API key configured")
else:
    CHAT_ENABLED = False
    logger.warning("OpenAI API key not found - Chat features will be disabled")

# Initialize Flask
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Initialize Pico service
pico_service = PicoService()

@app.route('/')
def home():
    try:
        # First make a request to get current state
        response = pico_service.make_request('', "Home page request")
        status = response.text
        temperature = response.temperature
        logger.info(f"Home page - Status: {status}, Temperature: {temperature}")
        
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
        response = pico_service.make_request('light_on', "Turn ON request")
        logger.info(f"Light ON response - Status: {response.text}, Temp: {response.temperature}")
        return jsonify({
            'status': response.text,
            'temperature': response.temperature
        })
    except Exception as e:
        logger.error(f"Error turning light on: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/light_off')
def light_off():
    try:
        response = pico_service.make_request('light_off', "Turn OFF request")
        logger.info(f"Light OFF response - Status: {response.text}, Temp: {response.temperature}")
        return jsonify({
            'status': response.text,
            'temperature': response.temperature
        })
    except Exception as e:
        logger.error(f"Error turning light off: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/flash')
def flash():
    try:
        # Make the request and get updated state
        response = pico_service.make_request('flash', "Flash request")
        logger.info(f"Flash response - Status: {response.text}, Temp: {response.temperature}")
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error setting flash: {e}")
        return redirect(url_for('home'))

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
        logger.info("Starting Flask server...")
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")