# SUNY Broome WiFi Pico Project

## Project Overview
A web-based IoT (Internet of Things) system that enables remote control and monitoring of a Raspberry Pi Pico W through a secure web interface. The system provides real-time LED control and temperature monitoring through a multi-tier architecture, utilizing modern web technologies and cloud services.

## System Architecture
┌─────────────────┐
│ Web Browser │
│ User Interface │
└────────┬────────┘
│
│ HTTPS
▼
┌────────┴────────┐
│ PythonAnywhere │
│ Flask App │
└────────┬────────┘
│
│ HTTPS
▼
┌────────┴────────┐
│ Ngrok Tunnel │
│ Secure Gateway │
└────────┬────────┘
│
│ HTTP
▼
┌────────┴────────┐
│ Pico W │
│ MicroPython │
└─────────────────┘

## Features
- 🔌 Remote LED Control (On/Off/Flash)
- 🌡️ Real-time Temperature Monitoring
- 📊 Live Status Updates
- 🔒 Secure HTTPS Communication
- 📝 Comprehensive Logging
- 🔄 Automatic Error Recovery
- 📱 Mobile-Responsive Interface

## Project Structure
suny_broome_wifi_v0/
├── client/
│ ├── client.py # PythonAnywhere Flask application
│ ├── config.py # Configuration settings
│ ├── requirements.txt # Python dependencies
│ └── templates/ # HTML templates
│ └── index.html # Web interface
├── pico/
│ ├── main.py # Pico W web server
│ └── config.py # WiFi credentials
└── docs/
├── setup/
│ ├── pico.md # Pico setup guide
│ ├── ngrok.md # Ngrok configuration
│ └── python.md # PythonAnywhere setup
├── api.md # API documentation
├── architecture.md # System design details
└── troubleshoot.md # Common issues & solutions


## Quick Start Guide

### 1. Hardware Requirements
- Raspberry Pi Pico W
- Micro USB cable
- Computer for programming
- Stable internet connection

### 2. Software Requirements
- MicroPython for Pico W
- Python 3.8+ for PythonAnywhere
- Ngrok account (free tier available)
- PythonAnywhere account (paid tier recommended)

### 3. Setup Steps
1. [Complete Pico W Setup](docs/setup/pico.md)
   - Flash MicroPython
   - Configure WiFi
   - Deploy web server

2. [Configure Ngrok](docs/setup/ngrok.md)
   - Install Ngrok
   - Set up tunnel
   - Configure security

3. [Deploy to PythonAnywhere](docs/setup/python.md)
   - Set up environment
   - Deploy Flask app
   - Configure web app

## Documentation

### Setup Guides
- [Detailed Pico Setup](docs/setup/pico.md)
- [Ngrok Configuration](docs/setup/ngrok.md)
- [PythonAnywhere Deployment](docs/setup/python.md)

### Technical Documentation
- [System Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Configuration Guide](docs/configuration.md)
- [Troubleshooting Guide](docs/troubleshoot.md)

## Dependencies

### Pico W
```python
# requirements-pico.txt
micropython-picozero
```

### PythonAnywhere
```python
# requirements.txt
flask==2.0.1
requests==2.26.0
python-dotenv==0.19.0
urllib3==1.26.7
```

## Common Issues & Solutions
See our [Troubleshooting Guide](docs/troubleshoot.md) for help with:
- Ngrok connection issues
- PythonAnywhere deployment
- Pico W WiFi connectivity
- LED control problems
- Temperature sensor readings

## Development

### Running Locally
1. Set up virtual environment
2. Install dependencies
3. Configure environment variables
4. Run Flask development server

### Deployment
1. Update PythonAnywhere:
   ```bash
   git pull
   pip install -r requirements.txt
   touch /var/www/web_app_name_wsgi.py
   ```

## Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## Security Notes
- All passwords should be stored in config files
- Use HTTPS for all web traffic
- Keep Ngrok authentication tokens secure
- Regularly update dependencies

## License
[MIT License](LICENSE)

## Acknowledgments
- SUNY Broome Computer Science Department
- Professor Grace
- Open Source Community

## Contact & Support
- [Project Issues](https://github.com/AlexandraBouillon/suny_broome_wifi_v0/issues)
- [Documentation Updates](docs/README.md)
- Email: bouillonam@acad.sunybroome.edu