

# Installing Thonny IDE

## 1. Download Thonny
- Go to [https://thonny.org/](https://thonny.org/)
- Click the download button for your operating system:
  - **Windows**: Download the Windows installer
  - **Mac**: Download the macOS version
  - **Linux**: Use your package manager or download the Linux version

## 2. Install Thonny

### Windows
1. Double-click the downloaded `.exe` file
2. Follow the installation wizard
3. Accept the default options (unless you have specific preferences)

### macOS
1. Open the downloaded `.pkg` file
2. Follow the installation wizard
3. You might need to go to `System Preferences → Security & Privacy` to allow the installation

### Linux
Using package manager:
```bash
sudo apt install thonny    # For Ubuntu/Debian
# or
sudo dnf install thonny    # For Fedora
```

## 3. First Launch
- Launch Thonny from your applications menu
- On first launch, it will ask about your preferred initial settings
- Choose "Standard" mode unless you have specific needs

## 4. Connect to Pico W
1. Plug your Pico W into your computer via USB
2. In Thonny, click on the bottom right corner where it says "Python"
3. Select "MicroPython (Raspberry Pi Pico)"
4. If you don't see your Pico:
   - Try a different USB port
   - Use a different USB cable (some cables are power-only)

## 5. Verify Connection
- You should see the MicroPython REPL (`>>>` prompt) in Thonny's Shell window
- If you don't see this, try clicking the Stop/Restart button (red square) in Thonny

## Next Steps
Once installed, you can:
- Open your `server.py` file in Thonny
- Click the green "Play" button to run it
- Watch the Shell window for the IP address output

> **Note**: If this is the first time using your Pico W, you might need to flash MicroPython onto it. Let me know if you need instructions for that step!



# How to Flash MicroPython onto Raspberry Pi Pico W

## 1. Download MicroPython
1. Go to the [official Raspberry Pi Pico W downloads page](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
2. Download the latest MicroPython UF2 file for Pico W
   - Look for a file named something like `micropython-firmware-pico-w.uf2`
   - **Important**: Make sure you download the Pico **W** version, not the regular Pico version

## 2. Prepare Your Pico W
1. Locate the `BOOTSEL` button on your Pico W
   - It's a small white button on the board
2. Hold down the `BOOTSEL` button
3. While holding the button, plug your Pico W into your computer via USB
4. Release the `BOOTSEL` button

## 3. Flash MicroPython
1. Your Pico W should appear as a USB mass storage device
   - On Windows: It shows up as "RPI-RP2" drive
   - On Mac: It appears as "RPI-RP2" volume
   - On Linux: It mounts automatically as "RPI-RP2"
2. Drag and drop (or copy) the downloaded `.uf2` file onto the RPI-RP2 drive
3. The Pico W will automatically restart once the file is copied
   - The drive will disappear from your computer
   - This is normal and means the flashing was successful

## 4. Verify Installation
1. Open Thonny
2. Click on the bottom right corner where it says "Python"
3. Select "MicroPython (Raspberry Pi Pico)"
4. You should see the MicroPython welcome message in the Shell window:
````
MicroPython v1.xx.x-xx-xxxxxxxx-xx on 2023-xx-xx; Raspberry Pi Pico W with RP2040
>>> 
````

## Troubleshooting
If you don't see the Pico W in Thonny:
- Try a different USB cable (some cables are power-only)
- Try a different USB port
- Repeat the flashing process
- Make sure you downloaded the correct UF2 file for Pico W

## Next Steps
Once MicroPython is installed, you can:
1. Open your `server.py` file in Thonny
2. Save it to the Pico W (File → Save as... → Raspberry Pi Pico)
3. Run it to get the IP address

> **Note**: Remember to update the WiFi credentials in `server.py` with your network details before running it!
