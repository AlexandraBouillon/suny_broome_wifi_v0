import requests
import time

class PicoWClient:
    def __init__(self, ip_address):
        """Initialize the client with the Pico W's IP address"""
        self.base_url = f"http://{ip_address}"
    
    def turn_light_on(self):
        """Send request to turn the LED on"""
        try:
            response = requests.get(f"{self.base_url}/lighton")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error turning light on: {e}")
            return False

    def turn_light_off(self):
        """Send request to turn the LED off"""
        try:
            response = requests.get(f"{self.base_url}/lightoff")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error turning light off: {e}")
            return False

    def flash_light(self):
        """Send request to flash the LED"""
        try:
            response = requests.get(f"{self.base_url}/flash")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error flashing light: {e}")
            return False

    def get_status(self):
        """Get the current temperature and LED state"""
        try:
            response = requests.get(self.base_url)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error getting status: {e}")
            return None

def main():
    pico_ip = input("Enter Pico W's IP address: ") # update with IP
    client = PicoWClient(pico_ip)

    while True:
        print("\nPico W Control Menu:")
        print("1. Turn LED On")
        print("2. Turn LED Off")
        print("3. Flash LED")
        print("4. Get Status")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            if client.turn_light_on():
                print("LED turned on successfully")
            else:
                print("Failed to turn LED on")

        elif choice == '2':
            if client.turn_light_off():
                print("LED turned off successfully")
            else:
                print("Failed to turn LED off")

        elif choice == '3':
            if client.flash_light():
                print("LED flashing initiated")
            else:
                print("Failed to initiate LED flashing")

        elif choice == '4':
            status = client.get_status()
            if status:
                print("Current status:", status)
            else:
                print("Failed to get status")

        elif choice == '5':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

        time.sleep(1)

if __name__ == "__main__":
    main()