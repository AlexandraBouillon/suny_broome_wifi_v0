import requests
import urllib3
import os
import re
from config import Config, logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PicoService:
    def __init__(self):
        self.status = "OFF"
        self.temperature = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'ngrok-skip-browser-warning': 'true'
        }
    
    @property
    def pico_url(self):
        url = os.environ.get('NGROK_URL')
        if not url:
            logger.error("NGROK_URL not found in environment variables")
            return None
        return url.rstrip('/')
    
    def _parse_response(self, html_content):
        """Parse LED status and temperature from the HTML response"""
        try:
            # Look for LED Status in the status div
            status_match = re.search(r'<div class="status">LED Status: ([A-Z]+)</div>', html_content)
            if status_match:
                self.status = status_match.group(1)
                logger.info(f"Found LED status: {self.status}")
            
            # Look for Temperature in the temperature div
            temp_match = re.search(r'<div class="temperature">Temperature: ([\d.]+)°C</div>', html_content)
            if temp_match:
                self.temperature = float(temp_match.group(1))
                logger.info(f"Found temperature: {self.temperature}")
                
            return True
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return False
    
    def make_request(self, endpoint, description="Request"):
        """Make a request to the Pico via ngrok"""
        try:
            if not self.pico_url:
                logger.error("No NGROK_URL configured")
                return type('Response', (), {'text': 'OFF', 'status_code': 200, 'temperature': 0})()
                
            url = f"{self.pico_url}/{endpoint}"
            logger.info("\n" + "=" * 50)
            logger.info(f"Making {description} to URL: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, verify=False, timeout=5)
                logger.info(f"Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Set initial status based on endpoint
                    if endpoint == 'light_on':
                        self.status = "ON"
                    elif endpoint == 'light_off':
                        self.status = "OFF"
                    elif endpoint == 'flash':
                        self.status = "FLASH"
                    
                    # Parse the response HTML
                    self._parse_response(response.text)
                    logger.info(f"Final values - Status: {self.status}, Temperature: {self.temperature}")
                    
                    # Return custom response object
                    return type('Response', (), {
                        'text': self.status,
                        'status_code': 200,
                        'temperature': self.temperature
                    })()
                
                logger.error(f"Bad response status: {response.status_code}")
                return type('Response', (), {'text': 'OFF', 'status_code': response.status_code, 'temperature': 0})()
                
            except requests.exceptions.ConnectionError:
                logger.error("Connection failed - Check if ngrok tunnel is active")
                return type('Response', (), {'text': 'OFF', 'status_code': 200, 'temperature': 0})()
            except requests.exceptions.Timeout:
                logger.error("Request timed out")
                return type('Response', (), {'text': 'OFF', 'status_code': 200, 'temperature': 0})()
                
        except Exception as e:
            logger.error(f"Error in {description}: {type(e).__name__}: {str(e)}")
            return type('Response', (), {'text': 'OFF', 'status_code': 200, 'temperature': 0})() 