from flask import Flask, render_template, redirect, url_for, jsonify, request
from datetime import datetime
import os
from config import Config, logger
from services.chat_service import get_ai_response
from services.pico_service import PicoService

# Initialize Flask
app = Flask(__name__, 
           template_folder=Config.TEMPLATE_DIR,
           static_folder=Config.STATIC_DIR)

# Initialize Pico service
pico_service = PicoService()

@app.route('/')
def home():
    try:
        response = pico_service.make_request('', "Home page request")
        status = response.text.strip() if response else "OFF"
        # Ensure status is one of: ON, OFF, FLASH
        if status not in ['ON', 'OFF', 'FLASH']:
            status = 'OFF'
        logger.info(f"Current LED status: {status}")
        return render_template('index.html', 
                             status=status,
                             temperature=0,
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return render_template('index.html', 
                             status="OFF",
                             temperature=0,
                             now=datetime.now())

@app.route('/light_on')
def light_on():
    try:
        response = pico_service.make_request('light_on', "Turn ON request")
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error in light_on route: {str(e)}")
        return redirect(url_for('home'))

@app.route('/light_off')
def light_off():
    try:
        response = pico_service.make_request('light_off', "Turn OFF request")
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error in light_off route: {str(e)}")
        return redirect(url_for('home'))

@app.route('/flash')
def flash():
    try:
        response = pico_service.make_request('flash', "Flash request")
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Error in flash route: {str(e)}")
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
    app.run(debug=Config.DEBUG)