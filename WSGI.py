import sys
import os

 
path = '/home/SUNYBROOMEPROJECT/suny_broome_wifi_v0'
if path not in sys.path:
    sys.path.append(path)

# Import your Flask app
from client import app as application