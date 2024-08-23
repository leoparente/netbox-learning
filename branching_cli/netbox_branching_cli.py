import os
import requests
import argparse
from dotenv import load_dotenv
from tabulate import tabulate
import pprint

# Load environment variables from .env file
load_dotenv()

# Fetch variables from environment
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

def get_branches(branch_name=None):
    """
    Retrieves the list of branches from the NetBox API.
    If branch_name is provided, it filters the branches to return only the matching one.
    """
    if not NETBOX_URL or not NETBOX_TOKEN:
        print("Error: NETBOX_URL and NETBOX_TOKEN must be set in the .env file.")
        return None

    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    branches_endpoint = f"{NETBOX_URL}/api/plugins/branching/branches/"
    
    try:
        response = requests.get(branches_endpoint, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        return None
    except Exception as err:
        print(f"An error occurred: {err}")
        return None

    branches_data = response.json()
    branches = branches_data.get('results', [])
    
    if branch_name:
        # Filter branches to find the one with the specified name
        branches = [branch for branch in branches if branch['name'] == branch_name]
    
    return branches

def get_changes_count(branch_id):
    """
    Retrieves the number of changes for a specific branch by filtering the changes endpoint.
    """
    changes_endpoint = f"{NETBOX_URL}/api/plugins/branching/changes/"
    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.get(changes_endpoint, headers=headers)
        response.raise_for_status()
        changes_data = response.json()
        changes = changes_data.get('results', [])
        
        # Filter changes that belong to the given branch_id
        branch_changes = [change for change in changes if change['branch']['id'] == branch_id]
        return len(branch_changes)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        return "N/A"
    except Exception as err:
        print(f"An error occurred: {err}")
        return "N/A"

def create_branch(branch_name):
    """
    Creates a new branch with the given name.
    """
    if not NETBOX_URL or not NETBOX_TOKEN:
        print("Error: NETBOX_URL and NETBOX_TOKEN must be set in the .env file.")
        return None

    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    branches_endpoint = f"{NETBOX_URL}/api/plugins/branching/branches/"
    data = {
        "name": branch_name,
        "status": "ready"  # Adjust this according to the API requirements
    }
    
    try:
        response = requests.post(branches_endpoint, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        return None
    except Exception as err:
        print(f"An error occurred: {err}")
        return None

    branch = response.json()
    return branch

def delete_branch(branch_name):
    """
    Deletes a branch with the given name.
    """
    branches = get_branches(branch_name)
    if not branches:
        print(f"No branch found with name: {branch_name}")
        return

    branch = branches[0]
    branch_id = branch.get('id')
    
    delete_endpoint = f"{NETBOX_URL}/api/plugins/branching/branches/{branch_id}/"
    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.delete(delete_endpoint, headers=headers)
        response.raise_for_status()
        print(f"Branch '{branch_name}' deleted successfully.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"An error occurred: {err}")

def main():
    parser = argparse.ArgumentParser(description="NetBox Branch Management CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Subparser for 'ls' command (formerly 'get')
    parser_ls = subparsers.add_parser('ls', help='List branches')
    parser_ls.add_argument('branch_name', nargs='?', help='Name of the branch to retrieve')

    # Subparser for 'create' command
    parser_create = subparsers.add_parser('create', help='Create a branch')
    parser_create.add_argument('branch_name', help='Name of the branch to create')
    
    # Subparser for 'rm' command (formerly 'delete')
    parser_rm = subparsers.add_parser('rm', help='Remove (delete) a branch')
    parser_rm.add_argument('branch_name', help='Name of the branch to remove')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "ls":
        branches = get_branches(args.branch_name)
        if branches:
            table = []
            for branch in branches:
                branch_id = branch.get('id', 'N/A')
                branch_name = branch.get('name', 'N/A')
                status = branch.get('status', 'N/A')
                created_at = branch.get('created', 'N/A')

                # Get the number of changes associated with this branch
                changes_count = get_changes_count(branch_id)
                
                table.append([branch_id, branch_name, status, changes_count, created_at])

            headers = ["ID", "Name", "Status", "Changes", "Created At"]
            print(tabulate(table, headers, tablefmt="pretty"))
        else:
            print("No branches found or unexpected response format.")
    
    elif args.command == "create":
        branch = create_branch(args.branch_name)
        if branch:
            branch_id = branch.get('id', 'N/A')
            status = branch.get('status', 'N/A')

            # Get the number of changes associated with this branch
            changes_count = get_changes_count(branch_id)

            table = [[
                branch.get('id', 'N/A'),
                branch.get('name', 'N/A'),
                branch.get('status', 'N/A'),
                changes_count,
                branch.get('created', 'N/A')
            ]]
            headers = ["ID", "Name", "Status", "Changes", "Created At"]
            print(tabulate(table, headers, tablefmt="pretty"))
        else:
            print("Failed to create branch.")

    elif args.command == "rm":
        delete_branch(args.branch_name)

if __name__ == "__main__":
    main()