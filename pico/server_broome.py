from picozero import pico_temp_sensor, pico_led
from time import sleep
import machine
import network
import socket

# Import credentials - will fail if config.py is missing
# from config import WIFI_SSID, WIFI_PASSWORD

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)  # Turn off interface first
    sleep(1)
    wlan.active(True)   # Then turn it back on
    
    # Set power mode to improve connection stability
    wlan.config(pm = 0xa11140)  # Disable power-save mode
    
    print('Scanning for networks...')
    available_networks = wlan.scan()
    network_names = [net[0].decode('utf-8') for net in available_networks]
    print('Available networks:', network_names)
    
    if 'SBCCOpen' in network_names:
        print('SBCCOpen network found, attempting to connect...')
        wlan.connect('SBCCOpen')
        
        # Add timeout for connection attempts
        max_wait = 15
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print(f'Waiting for connection... ({max_wait} attempts left)')
            print('Connection status:', wlan.status())
            sleep(1)
        
        if wlan.isconnected():
            id = wlan.ifconfig()[0]
            print("Connected on ", id)
            return id
        else:
            print("Could not connect to SBCCOpen")
            print("Final status:", wlan.status())
            sleep(2)
            machine.reset()
    else:
        print('SBCCOpen network not found!')
        print('Available networks were:', network_names)
        sleep(2)
        machine.reset()

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print("connection = ", connection)
    return connection 

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
    temperature = pico_temp_sensor.temp  # Initial temperature reading
    print(f"Starting temperature: {temperature}°C")
    
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        # Get fresh temperature reading
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
        elif request == '/status':
            response = f'HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n{state}'
            client.send(response.encode())
            client.close()
            continue
            
        html = webpage(temperature, state)
        response = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + html
        client.send(response.encode())
        client.close()

try:
    wifi_id = wifi_connect()
    print("Connected on ", wifi_id)
    wifi_connection = open_socket(wifi_id)
    serve(wifi_connection)
    
except KeyboardInterrupt:
    machine.reset()

