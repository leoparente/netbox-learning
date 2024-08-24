import os
import requests
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch variables from environment
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

def create_site_in_branch(branch_name, site_name, site_slug):
    """
    Creates a new site in the specified branch using the branch context header.
    
    :param branch_name: The name of the branch where the site should be created.
    :param site_name: The name of the new site.
    :param site_slug: The slug (URL-friendly version) of the site name.
    """
    if not NETBOX_URL or not NETBOX_TOKEN or not branch_name:
        print("Error: Ensure that NETBOX_URL, NETBOX_TOKEN, and branch_name are set correctly.")
        return
    
    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Branch-Name": branch_name
    }
    
    site_endpoint = f"{NETBOX_URL}/api/dcim/sites/"
    
    data = {
        "name": site_name,
        "slug": site_slug
    }
    
    try:
        response = requests.post(site_endpoint, headers=headers, json=data)
        response.raise_for_status()
        print(f"Site '{site_name}' created successfully in branch '{branch_name}'.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new site in a NetBox branch.")
    
    # Adding command-line arguments
    parser.add_argument("--branch_name", help="The name of the branch where the site should be created.")
    parser.add_argument("--site_name", help="The name of the new site.")
    parser.add_argument("--site_slug", help="The slug (URL-friendly version) of the site name.")
    
    args = parser.parse_args()

    # Prompt for inputs if not provided as command-line arguments
    branch_name = args.branch_name or input("Enter the branch name: ")
    site_name = args.site_name or input("Enter the site name: ")
    site_slug = args.site_slug or input("Enter the site slug: ")

    create_site_in_branch(branch_name, site_name, site_slug)