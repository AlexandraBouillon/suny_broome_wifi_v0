from flask import Flask, render_template_string, redirect, url_for
import requests
import time

app = Flask(__name__)

class PicoWClient:
    def __init__(self):
        """Initialize the client with the Pico W's IP address"""
        self.base_url = "https://5472-2603-7081-5500-76ad-29f9-2637-ebbe-1e18.ngrok-free.app"
    
    def test_connection(self):
        """Test the connection to Pico W"""
        try:
            print(f"Testing connection to: {self.base_url}")
            response = requests.get(self.base_url, timeout=5)
            print(f"Connection test response: {response.status_code}")
            return True, "Connection successful"
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return False, "Cannot connect to Pico W - Check if Pico is running and IP is correct"
        except requests.exceptions.Timeout:
            print("Connection timeout")
            return False, "Connection timed out - Pico W not responding"
        except Exception as e:
            print(f"Unexpected error in test_connection: {str(e)}")
            return False, f"Unexpected error: {str(e)}"

    def turn_light_on(self):
        """Send request to turn the LED on"""
        try:
            print(f"Attempting to turn light on at: {self.base_url}/lighton?")
            response = requests.get(f"{self.base_url}/lighton?", timeout=5)
            print(f"Light on response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error turning light on: {str(e)}")
            return False

    def turn_light_off(self):
        """Send request to turn the LED off"""
        try:
            print(f"Attempting to turn light off at: {self.base_url}/lightoff?")
            response = requests.get(f"{self.base_url}/lightoff?", timeout=5)
            print(f"Light off response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error turning light off: {str(e)}")
            return False

    def flash_light(self):
        """Send request to flash the LED"""
        try:
            print(f"Attempting to flash light at: {self.base_url}/flash?")
            response = requests.get(f"{self.base_url}/flash?", timeout=5)
            print(f"Flash response: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error flashing light: {str(e)}")
            return False

    def get_status(self):
        """Get the current temperature and LED state"""
        try:
            print(f"Getting status from: {self.base_url}")
            response = requests.get(self.base_url, timeout=5)
            print(f"Status response: {response.status_code}")
            return response.text
        except Exception as e:
            print(f"Error getting status: {str(e)}")
            return f"Error connecting to Pico W: {str(e)}"

# Initialize the client
client = PicoWClient()

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
        .error {
            color: red;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Pico W Control Panel</h1>
    
    <div class="status">
        <h2>Connection Status:</h2>
        <p {% if not connection_ok %}class="error"{% endif %}>
            {{ connection_status }}
        </p>
    </div>

    {% if connection_ok %}
        <a href="{{ url_for('light_on') }}" class="button">Turn Light On</a>
        <a href="{{ url_for('light_off') }}" class="button">Turn Light Off</a>
        <a href="{{ url_for('flash') }}" class="button">Flash Light</a>
        
        <div class="status">
            <h2>Pico Status:</h2>
            <p>{{ status }}</p>
        </div>
    {% endif %}
    
    <p><a href="{{ url_for('index') }}" class="button">Refresh Status</a></p>
</body>
</html>
'''

@app.route('/')
def index():
    connection_ok, connection_status = client.test_connection()
    status = client.get_status() if connection_ok else None
    return render_template_string(HTML_TEMPLATE, 
                                connection_ok=connection_ok,
                                connection_status=connection_status,
                                status=status)

@app.route('/light_on')
def light_on():
    result = client.turn_light_on()
    print(f"Light on result: {result}")
    return redirect(url_for('index'))

@app.route('/light_off')
def light_off():
    result = client.turn_light_off()
    print(f"Light off result: {result}")
    return redirect(url_for('index'))

@app.route('/flash')
def flash():
    result = client.flash_light()
    print(f"Flash result: {result}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)