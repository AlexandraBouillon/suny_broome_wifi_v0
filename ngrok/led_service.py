from machine import Pin
import time
from config import Config, logger

class LEDService:
    def __init__(self):
        self.led = Pin("LED", Pin.OUT)
        self.status = "OFF"
        
    def turn_on(self):
        self.led.on()
        self.status = "ON"
        logger.info("LED turned ON")
        
    def turn_off(self):
        self.led.off()
        self.status = "OFF"
        logger.info("LED turned OFF")
        
    def flash(self):
        self.status = "FLASH"
        logger.info("LED set to FLASH")
        
    def get_status(self):
        return self.status