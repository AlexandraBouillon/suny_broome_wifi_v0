import requests
import urllib3
import os
from config import Config, logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PicoService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',  # Accept any content type
            'ngrok-skip-browser-warning': 'true'
        }
    
    @property
    def pico_url(self):
        url = os.environ.get('NGROK_URL')
        if not url:
            logger.error("NGROK_URL not found in environment variables")
            return None
        return url.rstrip('/')
    
    def make_request(self, endpoint, description="Request"):
        """Make a request to the Pico with standard headers and logging"""
        try:
            if not self.pico_url:
                logger.error("No NGROK_URL configured")
                return type('Response', (), {'text': 'OFF', 'status_code': 200})()
                
            url = f"{self.pico_url}/{endpoint.lstrip('/')}"
            logger.info("\n" + "=" * 50)
            logger.info(f"Making {description}")
            logger.info(f"URL: {url}")
            
            try:
                # Make request and get full response details
                response = requests.get(url, headers=self.headers, verify=False, timeout=5)
                
                logger.info(f"Response Status: {response.status_code}")
                logger.info(f"Response Headers: {dict(response.headers)}")
                logger.info(f"Response Content Type: {response.headers.get('content-type', 'unknown')}")
                logger.info(f"Response Text: {response.text[:200]}")  # First 200 chars
                logger.info(f"Response Length: {len(response.text)}")
                
                if response.status_code == 400:
                    # Try to get error details
                    try:
                        error_details = response.json()
                        logger.error(f"Error details: {error_details}")
                    except:
                        logger.error("Could not parse error response as JSON")
                    
                    return type('Response', (), {'text': 'OFF', 'status_code': 200})()
                
                return response
                
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {str(e)}")
                return type('Response', (), {'text': 'OFF', 'status_code': 200})()
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after 5 seconds")
                return type('Response', (), {'text': 'OFF', 'status_code': 200})()
                
        except Exception as e:
            logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
            return type('Response', (), {'text': 'OFF', 'status_code': 200})() 