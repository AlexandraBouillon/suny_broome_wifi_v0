import sys
import os

# Add the project directory to the Python path
path = '/home/SUNYBROOMEPROJECT/suny_broome_wifi_v0'
if path not in sys.path:
    sys.path.append(path)

from client import app as application