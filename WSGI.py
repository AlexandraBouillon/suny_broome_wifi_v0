import sys
import os

# Add the project root directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set environment variables directly (no sensitive data)
os.environ.update({
    # Use the exact working ngrok URL for both
    'NGROK_URL': 'https://d5b3-2603-7081-5500-76ad-b5b0-27bf-e53c-aa5e.ngrok-free.app',
    'PICO_URL': 'https://d5b3-2603-7081-5500-76ad-b5b0-27bf-e53c-aa5e.ngrok-free.app',
    'PORT': '5001'
})

# Debug print statements
print("Python path:", sys.path)
print("Project directory:", project_dir)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir(project_dir))

# Import the Flask app directly from server.py in root
from server import app as application 