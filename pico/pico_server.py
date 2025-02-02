from picozero import pico_temp_sensor, pico_led
from time import sleep
import machine
import network
import socket

# Import from local config.py
from config import WIFI_SSID, WIFI_PASSWORD

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    id = wlan.ifconfig()[0]
    print("Connected on ", id)
    return id

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
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        # Debug print
        print(f"Received request: {request}")
        
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
            # Just return the current state without HTML
            response = f'HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n{state}'
            client.send(response.encode())
            client.close()
            continue
            
        temperature = pico_temp_sensor.temp
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