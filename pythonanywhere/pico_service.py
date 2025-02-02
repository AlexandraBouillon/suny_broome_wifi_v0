import requests
import urllib3
from config import Config, logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PicoService:
    def __init__(self, pico_url):
        self.pico_url = pico_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'ngrok-skip-browser-warning': 'true'
        }
    
    def make_request(self, endpoint, description="Request"):
        """Make a request to the Pico with standard headers and logging"""
        try:
            url = f"{self.pico_url}/{endpoint}"
            logger.info("=" * 50)
            logger.info(f"{description}")
            logger.info(f"URL: {url}")
            
            response = requests.get(url, headers=self.headers, verify=False)
            logger.info(f"Response Status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error in {description}: {str(e)}")
            raise