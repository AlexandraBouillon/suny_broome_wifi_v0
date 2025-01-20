   # Script to automatically update config.py when ngrok starts
   import requests
   import json
   
   def update_ngrok_url():
       try:
           # Get the active tunnel URL from ngrok API
           response = requests.get('http://localhost:4040/api/tunnels')
           tunnels = json.loads(response.text)
           url = tunnels['tunnels'][0]['public_url']
           
           # Update config.py
           with open('config.py', 'r') as file:
               lines = file.readlines()
           
           with open('config.py', 'w') as file:
               for line in lines:
                   if line.startswith('NGROK_URL'):
                       file.write(f'NGROK_URL = "{url}"\n')
                   else:
                       file.write(line)
           
           print(f"Updated config.py with new URL: {url}")
       except Exception as e:
           print(f"Error updating URL: {e}")