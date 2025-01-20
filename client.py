from flask import Flask, redirect, url_for, render_template
import requests
import json

# Initialize Flask app
app = Flask(__name__)

# ESP32 URL (update with your ESP32's IP address)
ESP32_URL = "http://192.168.1.184"  # Update this with your ESP32's IP

def send_request(endpoint):
    """Helper function to send requests to ESP32"""
    try:
        response = requests.get(f"{ESP32_URL}/{endpoint}")
        return response.status_code == 200
    except:
        return False

@app.route('/')
def home():
    """Home page route"""
    try:
        # Try to get status from ESP32
        response = requests.get(f"{ESP32_URL}/status")
        if response.status_code == 200:
            status = response.json()
        else:
            status = {"led": "unknown", "message": "Error connecting to ESP32"}
    except:
        status = {"led": "unknown", "message": "Error connecting to ESP32"}
    
    return render_template('index.html', status=status)

@app.route('/light_on')
def light_on():
    """Turn light on route"""
    send_request('on')
    return redirect(url_for('home'))

@app.route('/light_off')
def light_off():
    """Turn light off route"""
    send_request('off')
    return redirect(url_for('home'))

@app.route('/flash')
def flash():
    """Flash light route"""
    send_request('flash')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')