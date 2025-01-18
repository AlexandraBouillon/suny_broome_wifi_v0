from picozero import pico_temp_sensor, pico_led
from time import sleep
import machine
import network
import socket

# WiFi credentials
ssid = 'SpectrumSetup-BB'
password = 'MAGGIEMAE'

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            
            <form action="lighton">
            <input type="submit" value="Light on" />
            </form>

            <form action="lightoff">
            <input type="submit" value="Light off" />
            </form>

            <form action="flash">
            <input type="submit" value="flash 3x" />
            </form>
            
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            
            </body>
            </html>
            """
    return str(html)

def wifi_connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

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
            print(f"Request: {request}")  # Debug print
            
            # Prepare response header
            response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
            
            if 'lighton?' in request:
                pico_led.on()
                state = 'ON'
                client.send(response.encode())
            elif 'lightoff?' in request:
                pico_led.off()
                state = 'OFF'
                client.send(response.encode())
            elif 'flash?' in request:
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
                state = 'FLASHED'
                client.send(response.encode())
            else:
                # Main page
                temperature = pico_temp_sensor.temp
                html = webpage(temperature, state)
                client.send(response.encode() + html.encode())
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()

try:
    ip = wifi_connect()
    connection = socket.socket()
    connection.bind((ip, 80))
    connection.listen(1)
    print(f"Listening on {ip}")
    serve(connection)
except KeyboardInterrupt:
    machine.reset()