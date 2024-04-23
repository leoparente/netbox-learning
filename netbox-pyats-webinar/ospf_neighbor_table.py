# filename: ospf_neighbor_table.py

# Description: Script to get and print OSPF Neighbor Table for a given device.
# Import the necessary libraries
from genie.testbed import load
from prettytable import PrettyTable

# Function to get and print OSPF Neighbor Table for a given device
def get_ospf_neighbor_table(device_name: str, testbed_file: str = 'testbed.yaml') -> None:
    """
    Function to get and print OSPF Neighbor Table for a given device.
    :param device_name: Name of the device
    :param testbed_file: Path to the testbed file
    :return: None
    """
    # Load the testbed
    testbed = load(testbed_file)

    # Get the device
    device = testbed.devices[device_name]

    # Connect to the device
    device.connect()

    # Parse the 'show ip ospf neighbor' command
    data = device.parse('show ip ospf neighbor')

    # Define the table
    table = PrettyTable()
    table.field_names = ["Interface", "Neighbor", "Address", "State"]

    # Iterate over the interfaces and neighbors
    for interface, details in data['interfaces'].items():
        for neighbor, neighbor_details in details['neighbors'].items():
            # Add a row to the table
            table.add_row([interface, neighbor, neighbor_details['address'], neighbor_details['state']])

    # Print the table for the device 
    print(f"OSPF Neighbor Table for {device.name}")
    print(table)

# Call the function with the device name
get_ospf_neighbor_table('CSR1')