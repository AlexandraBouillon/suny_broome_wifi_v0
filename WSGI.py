import sys
path = '/home/SUNYBROOMEPROJECT'  
if path not in sys.path:
    sys.path.append(path)

from client import app as application