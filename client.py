import requests
import time
from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

class PicoWClient:
    def __init__(self, ip_address):
        """Initialize the client with the Pico W's IP address"""
        self.base_url = f"http://{ip_address}"
    
    def turn_light_on(self):
        try:
            response = requests.get(f"{self.base_url}/lighton")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error turning light on: {e}")
            return False

    def turn_light_off(self):
        try:
            response = requests.get(f"{self.base_url}/lightoff")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error turning light off: {e}")
            return False

    def flash_light(self):
        try:
            response = requests.get(f"{self.base_url}/flash")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error flashing light: {e}")
            return False

    def get_status(self):
        try:
            response = requests.get(self.base_url)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error getting status: {e}")
            return None

 
client = PicoWClient('192.168.1.137')  

 
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Pico W Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 10px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Pico W Control Panel</h1>
    
    <a href="{{ url_for('light_on') }}" class="button">Turn Light On</a>
    <a href="{{ url_for('light_off') }}" class="button">Turn Light Off</a>
    <a href="{{ url_for('flash') }}" class="button">Flash Light</a>
    
    <div class="status">
        <h2>Status:</h2>
        <p>{{ status }}</p>
    </div>
    
    <p><a href="{{ url_for('index') }}" class="button">Refresh Status</a></p>
</body>
</html>
'''

@app.route('/')
def index():
    status = client.get_status()
    return render_template_string(HTML_TEMPLATE, status=status)

@app.route('/light_on')
def light_on():
    client.turn_light_on()
    return redirect(url_for('index'))

@app.route('/light_off')
def light_off():
    client.turn_light_off()
    return redirect(url_for('index'))

@app.route('/flash')
def flash():
    client.flash_light()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)