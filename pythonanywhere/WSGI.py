import os
import sys
from dotenv import load_dotenv

# Path to your project directory
path = '/home/SUNYBROOMEPROJECT/suny_broome_wifi_v0'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables from .env file
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

# Import your Flask app
from server import app as application