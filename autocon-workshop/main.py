import os
import sys
import requests
from datetime import datetime
from ping3 import ping

# Function to ping an IP address
def is_device_reachable(ip):
    response = ping(ip)
    return response is not None

def fetch_rendered_config(device_id, device_name, headers):
    url = f"{NETBOX_URL}/api/dcim/devices/{device_id}/render-config/"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def save_config_to_file(device_name, config_content, timestamp):
    directory = os.path.join("generated_configs", timestamp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{device_name}.txt")
    with open(file_path, "w") as file:
        file.write(config_content)
    print(f"Configuration for device {device_name} saved to {file_path}")

if __name__ == "__main__":
    NETBOX_URL = os.getenv("NETBOX_URL").strip()
    NETBOX_TOKEN = os.getenv("NETBOX_TOKEN").strip()

    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json; indent=4",
    }

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    devices = sys.argv[1:]
    for device_name in devices:
        print(f"Processing device: {device_name}")
        
        device_info_url = f"{NETBOX_URL}/api/dcim/devices/?name={device_name}"
        response = requests.get(device_info_url, headers=headers)
        response.raise_for_status()
        device_info = response.json()["results"][0]
        device_id = device_info["id"]
        device_ip = device_info["primary_ip"]["address"].split('/')[0]

        print(f"Found device {device_name}. Device Info: Management IP: {device_ip}")

        if not is_device_reachable(device_ip):
            print(f"Device {device_name} at IP {device_ip} is not reachable. Skipping...")
            continue

        try:
            rendered_config = fetch_rendered_config(device_id, device_name, headers)
            config_content = rendered_config.get("content", "")
            if not config_content:
                print(f"Rendered config for device {device_name} is empty or not found.")
                continue
            save_config_to_file(device_name, config_content, timestamp)
        except requests.exceptions.HTTPError as e:
            print(f"Error occurred while fetching or saving config for device {device_name}: {e.response.status_code} - {e.response.reason}")
        except Exception as e:
            print(f"Unexpected error occurred while processing device {device_name}: {e}")