import os
import sys
import requests
import logging
from datetime import datetime
from ping3 import ping
from napalm import get_network_driver
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed for self-signed certificates
urllib3.disable_warnings(InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_device_reachable(ip):
    response = ping(ip)
    return response is not None

def fetch_rendered_config(device_id, headers):
    url = f"{NETBOX_URL}/api/dcim/devices/{device_id}/render-config/"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def save_config_to_file(device_name, config_content):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    directory = os.path.join("configs", timestamp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{device_name}.txt")
    with open(file_path, "w") as file:
        file.write(config_content)
    logger.info(f"Configuration for device {device_name} saved to {file_path}")
    return file_path

def push_config_to_device(device_name, device_ip, config_file):
    try:
        driver = get_network_driver("srl")
        optional_args = {'insecure': True, 'inline_transfer': True}  # Add insecure and inline_transfer options
        device = driver(device_ip, NAPALM_USERNAME, NAPALM_PASSWORD, optional_args=optional_args)
        device.open()
        logger.info(f"Opened connection to device {device_name} at {device_ip}")
        facts = device.get_facts()
        logger.debug(f"Collected facts from device: {facts}")
        device.load_merge_candidate(filename=config_file)
        logger.debug(f"Loaded candidate config from {config_file}")
        diffs = device.compare_config()
        if diffs:
            logger.info(f"Config diffs for {device_name}: {diffs}")
            device.commit_config()
            logger.info(f"Configuration pushed to device {device_name} successfully.")
        else:
            logger.info(f"No changes needed for {device_name}.")
            device.discard_config()
        device.close()
    except Exception as e:
        logger.error(f"Failed to push configuration to device {device_name} at IP {device_ip}: {e}")

if __name__ == "__main__":
    NETBOX_URL = os.getenv("NETBOX_URL").strip()
    NETBOX_TOKEN = os.getenv("NETBOX_TOKEN").strip()
    NAPALM_USERNAME = os.getenv("NAPALM_USERNAME").strip()
    NAPALM_PASSWORD = os.getenv("NAPALM_PASSWORD").strip()

    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json; indent=4",
    }

    devices = sys.argv[1:]
    for device_name in devices:
        logger.info(f"Processing device: {device_name}")
        try:
            device_info_url = f"{NETBOX_URL}/api/dcim/devices/?name={device_name}"
            response = requests.get(device_info_url, headers=headers)
            response.raise_for_status()
            device_info = response.json()["results"][0]
            device_id = device_info["id"]
            device_ip = device_info["primary_ip"]["address"].split('/')[0]
            logger.info(f"Found device {device_name}. Device Info: Management IP: {device_ip}")

            if not is_device_reachable(device_ip):
                logger.warning(f"Device {device_name} at IP {device_ip} is not reachable. Skipping...")
                continue

            rendered_config = fetch_rendered_config(device_id, headers)
            config_content = rendered_config.get("content", "")
            if not config_content:
                logger.warning(f"Rendered config for device {device_name} is empty or not found.")
                continue
            config_file_path = save_config_to_file(device_name, config_content)
            push_config_to_device(device_name, device_ip, config_file_path)
        except Exception as e:
            logger.error(f"Error occurred while processing device {device_name}: {e}")