import sys
import os

# Add your project directory to Python path
path = '/home/sunybroomeproject/suny_broome_wifi_v0'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables directly (no sensitive data)
os.environ.update({
    'PICO_URL': 'https://c087-2603-7081-5500-76ad-a05b-eefb-6e6f-496b.ngrok-free.app',
    'NGROK_URL': 'https://c087-2603-7081-5500-76ad-a05b-eefb-6e6f-496b.ngrok-free.app',
    'PORT': '5001'
})

# Import your Flask app
from server import app as application