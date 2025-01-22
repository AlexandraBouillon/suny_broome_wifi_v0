import network
import socket
import time
import machine
from config import Secrets  # Simplified import for same directory
from microdot import Microdot, send_file
import json
from datetime import datetime
from handlers.perplexity_handler import PerplexityAPI  # Updated import path

# Load credentials from secrets
WIFI_SSID = Secrets.WIFI_SSID
WIFI_PASSWORD = Secrets.WIFI_PASSWORD

# Initialize LED and temperature sensor
led = machine.Pin("LED", machine.Pin.OUT)
sensor_temp = machine.ADC(4)

# Initialize web server
app = Microdot()
led_status = "OFF"

def connect_to_network():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection with timeout
        max_wait = 10
        while max_wait > 0 and not wlan.isconnected():
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)
            
    if wlan.isconnected():
        print('Connected! Network config:', wlan.ifconfig())
        return True
    print('Connection failed!')
    return False

@app.route('/')
def index(request):
    return send_file('templates/index.html', 
                    status_code=200, 
                    content_type='text/html')

@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        return 'Not found', 404
    return send_file(f'static/{path}')

@app.route('/light_on')
def light_on(request):
    global led_status
    led.on()
    led_status = "ON"
    return {'status': led_status}

@app.route('/light_off')
def light_off(request):
    global led_status
    led.off()
    led_status = "OFF"
    return {'status': led_status}

@app.route('/flash')
def flash(request):
    global led_status
    led.toggle()
    time.sleep(0.5)
    led.toggle()
    led_status = "OFF" if led.value() == 0 else "ON"
    return {'status': led_status}

@app.route('/status')
def status(request):
    # Read temperature
    reading = sensor_temp.read_u16() * 3.3 / (65535)
    temperature = 27 - (reading - 0.706)/0.001721
    
    return {
        'led_status': led_status,
        'temperature': f"{temperature:.1f}"
    }

def start_server():
    try:
        if connect_to_network():
            print("Starting web server...")
            app.run(port=80)
    except KeyboardInterrupt:
        print("Server stopped by user")
        machine.reset()
    except Exception as e:
        print(f"Error: {e}")
        machine.reset()

if __name__ == '__main__':
    start_server()