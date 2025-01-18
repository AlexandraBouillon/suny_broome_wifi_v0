from picozero import pico_temp_sensor, pico_led
from time import sleep
import machine
import network
import socket

# ssid = 'Grace'
# password = ''

# ssid = 'Grace5276'
# password = ''
ssid = 'SpectrumSetup-BB'
password = 'MAGGIEMAE'

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    id = wlan.ifconfig()[0]
    print("Connected on ",id)
    return id

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print("connection = ",connection)
    return connection 

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            
            <form action="/lighton">
            <input type="submit" value="Light on" />
            </form>

            <form action="/lightoff">
            <input type="submit" value="Light off" />
            </form>

            <form action="/flash">
            <input type="submit" value="flash 3x" />
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
        
##        print (request)
        
        try:
            request = request.split()[1]
        except IndexError:
            pass

        if request == 'lighton':
            pico_led.on()
            state = 'ON'
        if request =='lightoff':
            pico_led.off()
            state = 'OFF'
        if request =='flash':
            pico_led.on()
            sleep(1)
            pico_led.off()
            sleep(1)
            pico_led.on()
            sleep(1)
            pico_led.off()
            sleep(1)
            pico_led.on()
            sleep(1)
            pico_led.off()
            state = 'Flash'
        
        temperature = pico_temp_sensor.temp
        # html = webpage(temperature, state)
        # client.send(html)
        # client.close()
        response = f"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
        html = webpage(temperature, state)
        client.send(response.encode() + html.encode())
        client.close()
        
try:
    wifi_id = wifi_connect()
    print("Connected on ",wifi_id)
    wifi_connection = open_socket(wifi_id)
    serve(wifi_connection)
    
except KeyboardInterrupt:
    machine.reset()