import os
import sys
import requests
import logging
from datetime import datetime
from ping3 import ping
from napalm import get_network_driver
from urllib3.exceptions import InsecureRequestWarning
import urllib3
from difflib import unified_diff
import json

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

def save_config_to_file(directory, device_name, config_content):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f"{device_name}.txt")
    with open(file_path, "w") as file:
        file.write(config_content)
    logger.info(f"Configuration for device {device_name} saved to {file_path}")
    return file_path

def get_running_config(device, device_name, directory):
    running_config = device.get_config(retrieve="running")["running"]
    return save_config_to_file(directory, device_name, running_config)

def normalize_config(config_content):
    try:
        return json.dumps(json.loads(config_content), indent=2, sort_keys=True)
    except json.JSONDecodeError:
        return config_content

def push_config_to_device(device_name, device_ip, config_file, timestamp):
    try:
        driver = get_network_driver("srl")
        optional_args = {'insecure': True, 'inline_transfer': True}
        device = driver(device_ip, NAPALM_USERNAME, NAPALM_PASSWORD, optional_args=optional_args)
        device.open()
        logger.info(f"Opened connection to device {device_name} at {device_ip}")

        # Save the pre-change running config
        pre_change_dir = os.path.join("configs", timestamp, "running_pre")
        get_running_config(device, device_name, pre_change_dir)

        # Load and compare the new config
        device.load_merge_candidate(filename=config_file)
        logger.debug(f"Loaded merge candidate to device {device_name} at {device_ip}")
        diffs = device.compare_config()
        if diffs:
            logger.info(f"Config diffs for {device_name}: {diffs}")
            device.commit_config()
            logger.info(f"Configuration pushed to device {device_name} successfully.")
        else:
            logger.info(f"No changes needed for {device_name}.")
            device.discard_config()

        # Save the post-change running config
        post_change_dir = os.path.join("configs", timestamp, "running_post")
        post_change_file = get_running_config(device, device_name, post_change_dir)

        # Compare the post-change running config with the generated config
        with open(config_file, 'r') as generated_file:
            generated_config = normalize_config(generated_file.read())

        with open(post_change_file, 'r') as post_change_file:
            post_change_config = normalize_config(post_change_file.read())

        diff = unified_diff(generated_config.splitlines(), post_change_config.splitlines(), fromfile='generated', tofile='post_change')
        diff_output = '\n'.join(diff)

        if diff_output:
            diff_dir = os.path.join("configs", timestamp, "post_deploy_diffs")
            if not os.path.exists(diff_dir):
                os.makedirs(diff_dir)
            diff_file_path = os.path.join(diff_dir, f"{device_name}.txt")
            with open(diff_file_path, "w") as diff_file:
                diff_file.write(diff_output)
            logger.info(f"Differences between generated config and post-change running config for {device_name} saved to {diff_file_path}")
        else:
            logger.info(f"No differences between generated config and post-change running config for {device_name}")

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
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
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

            generated_config_dir = os.path.join("configs", timestamp, "generated")
            config_file_path = save_config_to_file(generated_config_dir, device_name, config_content)

            push_config_to_device(device_name, device_ip, config_file_path, timestamp)
        except Exception as e:
            logger.error(f"Error occurred while processing device {device_name}: {e}")