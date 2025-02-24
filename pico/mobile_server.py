from picozero import pico_temp_sensor, pico_led
from time import sleep
import machine
import network
import socket

# Import credentials - will fail if config.py is missing
# from config import WIFI_SSID, WIFI_PASSWORD

def wifi_connect():
    # Hardcoded credentials
    WIFI_SSID = "Robert"
    WIFI_PASSWORD = ""
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    sleep(1)
    wlan.active(True)
    
    # Set power mode to improve connection stability
    wlan.config(pm = 0xa11140)
    
    print('Scanning for networks...')
    available_networks = wlan.scan()
    network_names = [net[0].decode('utf-8') for net in available_networks]
    print('Available networks:', network_names)
    
    if WIFI_SSID in network_names:
        print(f'{WIFI_SSID} network found, attempting to connect...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Add more detailed status messages
        status_messages = {
            network.STAT_IDLE: "IDLE - No connection and no activity",
            network.STAT_CONNECTING: "CONNECTING - Connecting in progress",
            network.STAT_WRONG_PASSWORD: "WRONG PASSWORD - Failed due to incorrect password",
            network.STAT_NO_AP_FOUND: "NO AP FOUND - Failed because no access point replied",
            network.STAT_CONNECT_FAIL: "CONNECT FAIL - Failed due to other problems",
            network.STAT_GOT_IP: "GOT IP - Connection successful"
        }
        
        max_wait = 15
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            status = wlan.status()
            print(f'Waiting for connection... ({max_wait} attempts left)')
            print('Connection status:', status)
            status_msg = status_messages.get(status, f"Unknown status: {status}")
            print(f"Status: {status_msg}")
            sleep(1)
        
        if wlan.isconnected():
            # Get dynamic IP configuration from DHCP
            network_info = wlan.ifconfig()
            print("\nNetwork Configuration:")
            print(f"IP Address: {network_info[0]}")
            print(f"Subnet Mask: {network_info[1]}")
            print(f"Gateway: {network_info[2]}")
            print(f"DNS: {network_info[3]}")
            return network_info[0]  # Return the dynamically assigned IP
        else:
            print(f"Could not connect to {WIFI_SSID}")
            print("Final status:", wlan.status())
            sleep(2)
            machine.reset()
    else:
        print(f'{WIFI_SSID} network not found!')
        print('Available networks were:', network_names)
        sleep(2)
        machine.reset()

def open_socket(ip):
    port = 80  # Changed to port 80
    address = ('0.0.0.0', port)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        print(f"\nAttempting to create server on {ip}:{port}")
        print("Setting up socket options...")
        
        # Set socket to non-blocking mode
        connection.setblocking(False)
        
        print(f"Binding to all interfaces on port {port}...")
        connection.bind(address)
        print("Bind successful")
        
        print("Setting listen backlog...")
        connection.listen(1)
        print(f"Socket opened successfully")
        print(f"\nTry accessing http://{ip} in your browser")
        print("Make sure your device is connected to the hotspot!")
        
        return connection
        
    except OSError as e:
        print(f"\nSocket error occurred: {e}")
        print("Error details:")
        print(f"- Attempted to bind to port {port}")
        print("- Make sure no other service is using this port")
        sleep(2)
        machine.reset()

def webpage(temperature, state):
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <form action="./flash">
            <input type="submit" value="Flash" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    state = 'OFF'
    pico_led.off()
    temperature = pico_temp_sensor.temp
    print(f"Starting temperature: {temperature}°C")
    
    while True:
        try:
            client = None
            try:
                client, addr = connection.accept()
                print(f"Client connected from {addr}")
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN error
                    sleep(0.1)  # Small delay to prevent busy-waiting
                    continue
                else:
                    raise  # Re-raise if it's a different error
                
            if client is None:
                continue
                
            request = client.recv(1024)
            request = str(request)
            try:
                request = request.split()[1]
            except IndexError:
                pass
            
            temperature = pico_temp_sensor.temp
            print(f"Temperature: {temperature}°C")
            
            if request == '/lighton?' or request == '/lighton':
                pico_led.on()
                state = 'ON'
                print("Light turned ON")
            elif request == '/lightoff?' or request == '/lightoff':
                pico_led.off()
                state = 'OFF'
                print("Light turned OFF")
            elif request == '/flash?' or request == '/flash':
                for _ in range(5):
                    pico_led.on()
                    sleep(0.5)
                    pico_led.off()
                    sleep(0.5)
                state = 'OFF'
                print("Flash sequence completed")
            
            html = webpage(temperature, state)
            response = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + html
            client.send(response.encode())
            client.close()
            
        except Exception as e:
            print(f"Error in serve loop: {e}")
            if client:
                client.close()
            sleep(0.1)

try:
    wifi_id = wifi_connect()
    print("Connected on ", wifi_id)
    wifi_connection = open_socket(wifi_id)
    serve(wifi_connection)
    
except KeyboardInterrupt:
    machine.reset()


