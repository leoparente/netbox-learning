import sys
import time
import pynetbox
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

# Initialize pynetbox API
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# Define functions

def create_tags(tags):
    for tag in tags:
        try:
            existing_tag = nb.extras.tags.get(name=tag)
            if existing_tag:
                print(f"Tag '{tag}' already exists.")
            else:
                nb.extras.tags.create(name=tag, slug=tag.lower().replace(' ', '-'))
                print(f"Tag '{tag}' created successfully.")
        except Exception as e:
            print(f"Failed to create tag '{tag}': {e}")

def get_remote_data_source_id(remote_data):
    try:
        existing_source = nb.core.data_sources.get(name=remote_data['name'])
        if existing_source:
            print(f"Remote data source '{remote_data['name']}' already exists.")
            return existing_source.id
        else:
            data_source = nb.core.data_sources.create(remote_data)
            print(f"Remote data source '{remote_data['name']}' added successfully.")
            return data_source.id
    except Exception as e:
        print(f"Failed to add remote data source '{remote_data['name']}': {e}")
        return None

def sync_remote_data_source(data_source_id):
    try:
        response = requests.post(f"{NETBOX_URL}/api/core/data-sources/{data_source_id}/sync/", headers={"Authorization": f"Token {NETBOX_TOKEN}"})
        time.sleep(5)  # Sleep for 5 seconds to let the sync complete
        response.raise_for_status()
        print(f"Remote data source with ID {data_source_id} synced successfully.")
        return True
    except Exception as e:
        print(f"Failed to sync remote data source with ID {data_source_id}: {e}")
        return False

def get_latest_data_file(data_source_id):
    try:
        data_files = nb.core.data_files.filter(source_id=data_source_id)
        if data_files:
            for data_file in data_files:
                if data_file.path == "autocon-workshop/templates/device_template.j2":
                    print(f"Found matching data file: {data_file}")
                    return data_file
        print(f"Failed to find a matching data file for data source ID {data_source_id}")
        return None
    except Exception as e:
        print(f"Failed to retrieve data files for data source ID {data_source_id}: {e}")
        return None

def read_template_file(file):
    url = "https://raw.githubusercontent.com/netboxlabs/netbox-learning/develop/autocon-workshop/templates/device_template.j2"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            template_code = response.text
            print(f"Template code retrieved successfully")
            return template_code
        else:
            print(f"Failed to retrieve template code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve template code: {e}")

def create_config_template(template_name, template_code, data_file, auto_sync=True):
    try:
        existing_template = nb.extras.config_templates.get(name=template_name)
        if existing_template:
            print(f"Config template '{template_name}' already exists.")
            return
        config_template = nb.extras.config_templates.create(
            name=template_name,
            slug=template_name.lower().replace(' ', '-'),
            template_code=template_code,
            data_source=data_file.source.id,
            data_path=data_file.path,
            data_file=data_file.id,
            auto_sync=auto_sync  # Set auto_sync parameter
        )
        print(f"Config template '{template_name}' added successfully.")
        
        # Set auto_sync after creation
        if auto_sync:
            config_template.data_synced = True
            config_template.save()
    except Exception as e:
        print(f"Failed to add config template '{template_name}': {e}")

def delete_config_template(template_name):
    try:
        config_template = nb.extras.config_templates.get(name=template_name)
        if config_template:
            config_template.delete()
            print(f"Config template '{template_name}' deleted successfully.")
        else:
            print(f"Config template '{template_name}' not found.")
    except Exception as e:
        print(f"Failed to delete config template '{template_name}': {e}")

def delete_tags(tags):
    for tag in tags:
        try:
            tag_obj = nb.extras.tags.get(name=tag)
            if tag_obj:
                tag_obj.delete()
                print(f"Tag '{tag}' deleted successfully.")
            else:
                print(f"Tag '{tag}' not found.")
        except Exception as e:
            print(f"Failed to delete tag '{tag}': {e}")

def delete_remote_data_source(data_source_name):
    try:
        data_sources = nb.core.data_sources.filter(name=data_source_name)
        for ds in data_sources:
            ds.delete()
            print(f"Remote data source '{data_source_name}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete remote data source '{data_source_name}': {e}")

if __name__ == "__main__":
    action = sys.argv[1]
    device1 = sys.argv[2]
    device2 = sys.argv[3]

    print(f"Action: {action}")
    print(f"Device 1: {device1}")
    print(f"Device 2: {device2}")

    tags = ["Broadcast", "Point-to-Point"]
    remote_data = {
        "name": "Autocon Workshop",
        "slug": "autocon-workshop",
        "type": "git",
        "source_url": "https://github.com/netboxlabs/netbox-learning",
    }

    config_template_name = "Nokia SR Linux"

    if action == "CREATE":
        print("Starting CREATE operation...")
        create_tags(tags)
        data_source_id = get_remote_data_source_id(remote_data)
        if data_source_id:
            if sync_remote_data_source(data_source_id):
                latest_data_file = get_latest_data_file(data_source_id)
                if latest_data_file:
                    template_code = read_template_file(latest_data_file)
                    if template_code:
                        create_config_template(config_template_name, template_code, latest_data_file)
                    else:
                        print("Failed to read template file.")
                else:
                    print("Failed to retrieve the latest data file.")
        else:
            print("Failed to retrieve data source ID.")
    elif action == "DELETE":
        print("Starting DELETE operation...")
        delete_config_template(config_template_name)
        delete_tags(tags)
        delete_remote_data_source(remote_data["name"])
    else:
        print("Invalid action provided.")