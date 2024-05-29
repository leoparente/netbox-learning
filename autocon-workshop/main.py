import os
import sys
import requests
import pynetbox
import json
import datetime
from napalm import get_network_driver

# Get environment variables and clean any extra quotes or spaces
NETBOX_URL = os.getenv('NETBOX_URL', '').strip().strip('"').strip("'").strip('/')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN', '').strip().strip('"').strip("'")

# Debug prints for environment variables
print(f"Cleaned NETBOX_URL: {NETBOX_URL}")
print(f"Cleaned NETBOX_TOKEN: {NETBOX_TOKEN}")

# Check if the environment variables are correctly set
if not NETBOX_URL or not NETBOX_TOKEN:
    print("Error: NETBOX_URL or NETBOX_TOKEN environment variable is not set.")
    sys.exit(1)

# Initialize the NetBox API connection
try:
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
    print(f"Connected to NetBox API successfully at {NETBOX_URL}")
except Exception as e:
    print(f"Failed to connect to NetBox API: {e}")
    sys.exit(1)

def get_device_info(device_name):
    print(f"Fetching device info for {device_name}")
    device = nb.dcim.devices.get(name=device_name)
    if not device:
        raise ValueError(f"Device {device_name} not found in NetBox")
    mgmt_ip = device.primary_ip4.address if device.primary_ip4 else "No management IP"
    platform = device.platform.slug if device.platform else "No platform"
    print(f"Found device {device_name}. Device Info: Management IP: {mgmt_ip}, Platform: {platform}, Full Info: {device}")
    return device

def get_rendered_config(device):
    print(f"Fetching rendered config for device ID {device.id}")
    headers = {
        'Authorization': f'Token {NETBOX_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json; indent=4'
    }
    url = f"{NETBOX_URL}/api/dcim/devices/{device.id}/render-config/"
    response = requests.post(url, headers=headers, json={"extra_data": "abc123"})
    if response.status_code != 200:
        raise ValueError(f"Rendered config for device {device.name} not found in NetBox")
    print(f"Rendered config for device {device.name} fetched successfully.")
    return response.json().get('content')

def save_config_to_file(device_name, config):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    directory = "/configs"  # Save to the mapped directory
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{device_name}.txt")
    with open(file_path, 'w') as file:
        file.write(config)
    print(f"Configuration for device {device_name} saved to {file_path}")

def push_config(mgmt_ip, platform, config):
    print(f"Using NAPALM driver for platform {platform}")
    driver = get_network_driver(platform)
    device = driver(mgmt_ip, os.getenv('NAPALM_USERNAME'), os.getenv('NAPALM_PASSWORD'))
    print(f"Connecting to device {mgmt_ip}")
    
    try:
        device.open()
        print(f"Connected to device {mgmt_ip}")
        device.load_merge_candidate(config=config)
        print("Configuration loaded. Committing config...")
        device.commit_config()
        print("Configuration committed successfully.")
    except Exception as e:
        print(f"Error during configuration push: {e}")
        device.rollback()
        print("Configuration rollback completed.")
        raise e
    finally:
        device.close()
        print(f"Connection to device {mgmt_ip} closed.")

def main(device_names):
    for device_name in device_names:
        print(f"Processing device: {device_name}")
        try:
            device_info = get_device_info(device_name)
            mgmt_ip = device_info.primary_ip4.address.split('/')[0]
            platform = device_info.platform.slug
            
            print(f"Fetching rendered config for {device_name}")
            rendered_config = get_rendered_config(device_info)
            save_config_to_file(device_name, rendered_config)
            
            print(f"Pushing config to {device_name} at {mgmt_ip}")
            push_config(mgmt_ip, platform, rendered_config)
            print(f"Successfully pushed config to {device_name}")
        
        except Exception as err:
            print(f"Error occurred: {err}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <device1> <device2> ...")
        sys.exit(1)
    
    device_names = sys.argv[1:]
    main(device_names)