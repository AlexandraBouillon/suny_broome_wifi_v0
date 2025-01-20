# Raspberry Pi Pico W Setup Guide

## Hardware Requirements
- Raspberry Pi Pico W
- Micro USB cable
- Computer for programming

## Initial Setup
1. Download MicroPython UF2 file
   ```bash
   wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2
   ```

2. Connect Pico W in bootloader mode:
   - Hold BOOTSEL button
   - Connect USB while holding BOOTSEL
   - Release BOOTSEL after connecting

3. Copy UF2 file to Pico
   - Drag UF2 file to RPI-RP2 drive
   - Wait for reboot

## Software Setup

### Required Files
1. config.py for WiFi credentials:
   ```python
   WIFI_SSID = "your_ssid"
   WIFI_PASSWORD = "your_password"
   ```

2. main.py for web server:
   ```python
   from picozero import pico_temp_sensor, pico_led
   import network
   import socket
   from time import sleep
   
   # Import credentials
   from config import WIFI_SSID, WIFI_PASSWORD
   ```

### Installation Steps
1. Install Thonny IDE
   - Download from: https://thonny.org
   - Install for your operating system
   - Select MicroPython (Raspberry Pi Pico) as interpreter

2. Connect to Pico through Thonny
   - Open Thonny
   - Click "View" -> "Files"
   - Select your Pico from the interpreter menu

3. Upload Files
   - Copy config.py to Pico
   - Copy main.py to Pico
   - Verify files are listed in Pico's file browser

## Testing

### 1. WiFi Connection
```python
# In Thonny's shell:
import network
wlan = network.WLAN(network.STA_IF)
print(f"Connected: {wlan.isconnected()}")
print(f"IP Address: {wlan.ifconfig()[0]}")
```

### 2. LED Test
```python
# In Thonny's shell:
from picozero import pico_led
pico_led.on()
from time import sleep
sleep(1)
pico_led.off()
```

### 3. Temperature Sensor
```python
# In Thonny's shell:
from picozero import pico_temp_sensor
print(f"Temperature: {pico_temp_sensor.temp}°C")
```

## Troubleshooting

### WiFi Connection Issues
1. Credentials Check
   ```python
   print(f"SSID: {WIFI_SSID}")
   # Should match your network name
   ```

2. Signal Strength
   ```python
   print(f"Signal: {wlan.status()}")
   # 3 = Connected
   ```

3. Common Solutions:
   - Reset Pico (press reset button)
   - Check WiFi password
   - Move closer to router
   - Verify 2.4GHz network (Pico W doesn't support 5GHz)

### LED Problems
1. Pin Check
   ```python
   # LED should be on pin 25
   from machine import Pin
   led = Pin("LED", Pin.OUT)
   led.on()
   ```

2. Web Server Check
   ```python
   # Check if server is running
   import socket
   print(socket.socket())
   ```

### Temperature Sensor Issues
1. Sensor Test
   ```python
   # Raw sensor reading
   import machine
   sensor_temp = machine.ADC(4)
   reading = sensor_temp.read_u16() * (3.3 / 65535)
   temperature = 27 - (reading - 0.706)/0.001721
   print(f"Raw Temperature: {temperature}°C")
   ```

## Additional Resources
- [Official Pico W Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [MicroPython Documentation](https://docs.micropython.org/en/latest/rp2/quick