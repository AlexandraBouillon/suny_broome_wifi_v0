from flask import Flask, jsonify
from machine import Pin
import time
import gc
import network

# Initialize Flask app
app = Flask(__name__)

# Set up LED
led = Pin(2, Pin.OUT)

# WiFi credentials
WIFI_SSID = "SpectrumSetup-BB"
WIFI_PASSWORD = "MAGGIEMAE"

def connect_wifi():
    """Connect to WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())

@app.route('/')
def home():
    """Home route"""
    gc.collect()  # Run garbage collection
    return jsonify({
        "message": "ESP32 LED Control Server",
        "status": "running"
    })

@app.route('/on')
def on():
    """Turn LED on"""
    try:
        led.value(1)
        return jsonify({
            "led": "on",
            "message": "LED turned on"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to turn LED on"
        }), 500

@app.route('/off')
def off():
    """Turn LED off"""
    try:
        led.value(0)
        return jsonify({
            "led": "off",
            "message": "LED turned off"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to turn LED off"
        }), 500

@app.route('/flash')
def flash():
    """Flash LED once"""
    try:
        led.value(1)
        time.sleep(0.5)
        led.value(0)
        return jsonify({
            "led": "flashed",
            "message": "LED flashed"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to flash LED"
        }), 500

@app.route('/status')
def status():
    """Get LED status"""
    try:
        current_state = led.value()
        return jsonify({
            "led": "on" if current_state else "off",
            "message": "LED is " + ("on" if current_state else "off")
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to get LED status"
        }), 500

if __name__ == '__main__':
    try:
        # Connect to WiFi
        connect_wifi()
        
        # Start server
        print('Starting server...')
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        print('Failed to start server:', str(e))