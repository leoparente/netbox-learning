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

def get_changes_and_conflicts(branch_id):
    """
    Retrieves the number of changes and conflicts for a specific branch by filtering the changes endpoint.
    Returns a tuple: (number_of_changes, number_of_conflicts, conflicts_details)
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
        number_of_changes = len(branch_changes)

        # Gather conflict details
        conflicts_details = []
        for change in branch_changes:
            if change.get('conflicts'):
                for conflict in change['conflicts']:
                    conflicts_details.append({
                        'object_name': change['object']['name'],
                        'original': change['diff']['original'].get(conflict, 'N/A'),
                        'branch': change['diff']['modified'].get(conflict, 'N/A'),
                        'main': change['diff']['current'].get(conflict, 'N/A')
                    })

        number_of_conflicts = len(conflicts_details)

        return number_of_changes, number_of_conflicts, conflicts_details
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        return "N/A", "N/A", []
    except Exception as err:
        print(f"An error occurred: {err}")
        return "N/A", "N/A", []

def merge_branch(branch_name):
    """
    Merges the branch with the given name.
    """
    branches = get_branches(branch_name)
    if not branches:
        print(f"No branch found with name: {branch_name}")
        return

    branch = branches[0]
    branch_id = branch.get('id')

    # Check for changes and conflicts
    changes_count, conflicts_count, conflicts_details = get_changes_and_conflicts(branch_id)

    if conflicts_count > 0:
        print(f"You are attempting to merge branch {branch_name} which has {conflicts_count} conflicts:")
        print(tabulate(
            [
                [conflict['object_name'], conflict['original'], conflict['branch'], conflict['main']]
                for conflict in conflicts_details
            ],
            headers=["Object", "Main (original)", "Branch (current)", "Main (current)"],
            tablefmt="pretty"
        ))

        confirm = input(f"Do you want to proceed with the merge? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Merge aborted.")
            return

    merge_endpoint = f"{NETBOX_URL}/api/plugins/branching/branches/{branch_id}/merge/"
    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Include the commit parameter
    data = {
        "commit": True
    }

    try:
        response = requests.post(merge_endpoint, headers=headers, json=data)
        response.raise_for_status()
        print(f"Branch '{branch_name}' merged successfully.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"An error occurred: {err}")

def sync_branch(branch_name):
    """
    Syncs the branch with the given name.
    """
    branches = get_branches(branch_name)
    if not branches:
        print(f"No branch found with name: {branch_name}")
        return

    branch = branches[0]
    branch_id = branch.get('id')

    # Check for changes and conflicts
    changes_count, conflicts_count, conflicts_details = get_changes_and_conflicts(branch_id)

    if conflicts_count > 0:
        print(f"You are attempting to sync branch {branch_name} which has {conflicts_count} conflicts:")
        print(tabulate(
            [
                [conflict['object_name'], conflict['original'], conflict['branch'], conflict['main']]
                for conflict in conflicts_details
            ],
            headers=["Object", "Main (original)", "Branch (current)", "Main (current)"],
            tablefmt="pretty"
        ))

        confirm = input(f"Do you want to proceed with the sync? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Sync aborted.")
            return

    sync_endpoint = f"{NETBOX_URL}/api/plugins/branching/branches/{branch_id}/sync/"
    headers = {
        "Authorization": f"Token {NETBOX_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Include the commit parameter
    data = {
        "commit": True
    }

    try:
        response = requests.post(sync_endpoint, headers=headers, json=data)
        response.raise_for_status()
        print(f"Branch '{branch_name}' synced successfully.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"An error occurred: {err}")

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

    # Subparser for 'sync' command
    parser_sync = subparsers.add_parser('sync', help='Sync a branch')
    parser_sync.add_argument('branch_name', help='Name of the branch to sync')

    # Subparser for 'merge' command
    parser_merge = subparsers.add_parser('merge', help='Merge a branch')
    parser_merge.add_argument('branch_name', help='Name of the branch to merge')

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

                # Get the number of changes and conflicts associated with this branch
                changes_count, conflicts_count, _ = get_changes_and_conflicts(branch_id)
                
                table.append([branch_id, branch_name, status, changes_count, conflicts_count, created_at])

            headers = ["ID", "Name", "Status", "Changes", "Conflicts", "Created At"]
            print(tabulate(table, headers, tablefmt="pretty"))
        else:
            print("No branches found or unexpected response format.")
    
    elif args.command == "create":
        branch = create_branch(args.branch_name)
        if branch:
            branch_id = branch.get('id', 'N/A')
            status = branch.get('status', 'N/A')

            # Get the number of changes and conflicts associated with this branch
            changes_count, conflicts_count, _ = get_changes_and_conflicts(branch_id)

            table = [[
                branch.get('id', 'N/A'),
                branch.get('name', 'N/A'),
                branch.get('status', 'N/A'),
                changes_count,
                conflicts_count,
                branch.get('created', 'N/A')
            ]]
            headers = ["ID", "Name", "Status", "Changes", "Conflicts", "Created At"]
            print(tabulate(table, headers, tablefmt="pretty"))
        else:
            print("Failed to create branch.")

    elif args.command == "rm":
        delete_branch(args.branch_name)

    elif args.command == "sync":
        sync_branch(args.branch_name)

    elif args.command == "merge":
        merge_branch(args.branch_name)

if __name__ == "__main__":
    main()