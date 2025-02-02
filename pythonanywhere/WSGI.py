import sys
import os

# Add your project directory to Python path
path = '/home/SUNYBROOMEPROJECT/suny_broome_wifi_v0'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables with the exact working ngrok URL
os.environ['PICO_URL'] = 'https://d5b3-2603-7081-5500-76ad-b5b0-27bf-e53c-aa5e.ngrok-free.app'
os.environ['NGROK_URL'] = 'https://d5b3-2603-7081-5500-76ad-b5b0-27bf-e53c-aa5e.ngrok-free.app'

# Debug print
print(f"PICO_URL set to: {os.environ.get('PICO_URL')}")
print(f"NGROK_URL set to: {os.environ.get('NGROK_URL')}")

from server import app as application