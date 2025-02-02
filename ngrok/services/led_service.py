import logging
import requests
import os
from dotenv import load_dotenv
from time import sleep

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LEDService:
    def __init__(self):
        self.status = "OFF"
        self.temperature = 0
        self.pico_url = "http://192.168.1.137"  # Pico's static IP
        logger.info(f"LED Service initialized with Pico URL: {self.pico_url}")
        
    def _make_pico_request(self, endpoint):
        """Make a request to the Pico"""
        try:
            url = f"{self.pico_url}/{endpoint}?"
            logger.info(f"Making request to Pico: {url}")
            
            response = requests.get(url, timeout=5)
            logger.info(f"Pico response status: {response.status_code}")
            logger.info(f"Pico response text: {response.text}")
            
            if response.status_code == 200:
                # Parse status from response
                state_start = response.text.find("LED is ") + len("LED is ")
                state_end = response.text.find("</p>", state_start)
                if state_start > -1 and state_end > -1:
                    self.status = response.text[state_start:state_end]
                    
                return self.status
            else:
                logger.error(f"Pico returned status code: {response.status_code}")
                return None
                
        except requests.exceptions.ReadTimeout:
            # Don't change status on timeout for regular requests
            logger.error("Timeout while communicating with Pico")
            return None
        except Exception as e:
            logger.error(f"Error communicating with Pico: {type(e).__name__}: {str(e)}")
            return None
        
    def turn_on(self):
        try:
            pico_status = self._make_pico_request('lighton')
            if pico_status:
                self.status = "ON"
            logger.info(f"LED turned ON, Pico status: {pico_status}")
            return self.status
        except Exception as e:
            logger.error(f"Error turning LED on: {e}")
            return "ERROR"
        
    def turn_off(self):
        try:
            pico_status = self._make_pico_request('lightoff')
            if pico_status:
                self.status = "OFF"
            logger.info(f"LED turned OFF, Pico status: {pico_status}")
            return self.status
        except Exception as e:
            logger.error(f"Error turning LED off: {e}")
            return "ERROR"
        
    def flash(self):
        try:
            # First update our local status
            self.status = "FLASHING"
            
            # Then send the flash command to Pico
            pico_status = self._make_pico_request('flash')
            
            # After flash completes, get the current status
            self.status = self._make_pico_request('')
            
            logger.info(f"Flash sequence completed, final status: {self.status}")
            return self.status
        except Exception as e:
            logger.error(f"Error setting LED to flash: {e}")
            return "ERROR"
        
    def get_status(self):
        try:
            self._make_pico_request('')  # Get latest status and temperature
            return self.status
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return self.status
            
    def get_temperature(self):
        try:
            self._make_pico_request('')  # Get latest status and temperature
            return self.temperature
        except Exception as e:
            logger.error(f"Error getting temperature: {e}")
            return self.temperature