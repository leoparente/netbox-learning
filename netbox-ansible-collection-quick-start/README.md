# NetBox Ansible Collection - Quick Start

Ansible playbooks to get started working with the Ansible Collection for Netbox. This repo accompanies the talks given at Cisco Live Las Vegas 2024, by the Netbox Labs and Red Hat Network Automation product teams.

![netbox ansible collection](images/ansible_collection.png)

## Collection Overview

The collection is available from either [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/netbox/netbox/), or NetBox Labs and Red Hat customers can access the certified collection which is supported by both Red Hat and NetBox Labs, via [Ansible Automation Hub]. This doc is based on the Galaxy installation and shows how oto run the collection from  the command line, rather than from within Ansible Automation hub.

The NetBox Ansible project provides an Ansible collection for interacting with NetBox, the leading solution for modeling and documenting modern networks. By combining the traditional disciplines of IP address management (IPAM) and datacenter infrastructure management (DCIM) with powerful APIs and extensions, NetBox provides the ideal "source of truth" to power network automation.

This Ansible collection consists of a set of modules to define the intended network state in NetBox, along with plugins to drive automation of the network using data from NetBox.

## Requirements

- You must be running one of the two most recent releases of NetBox
- A NetBox write-enabled API token when using modules or a read-only token for the `nb_lookup ` and `nb_inventory` plugins.
- Python 3.10+
- Python modules:
  - pytz
  - pynetbox
- Ansible 2.15+

## Getting Started with the Collection

### Installation and Setup Using the Command Line

1. Clone the Git repo and change into the `netbox-ansible-collection-quick-start` directory:
    ```
    git clone https://github.com/netboxlabs/netbox-learning.git
    cd netbox-learning/netbox-ansible-collection-quick-start
    ```
2. Create and activate Python 3 virtual environment:
    ```
    python3 -m venv ./venv
    source venv/bin/activate
    ```
3. Install required Python packages. The command below will install the colllection
    ```
    pip install -r requirements.txt
    ```
4. Set environment variables for the NetBox API token and URL:
    ```
    export NETBOX_API=<YOUR_NETBOX_URL> (note - must include http:// or https://)
    export NETBOX_TOKEN=<YOUR_NETBOX_API_TOKEN>
    ```
### NetBox as a Dynamic Inventory Source for Ansible

The [Inventory Plugin](https://docs.ansible.com/ansible/latest/collections/netbox/netbox/nb_inventory_inventory.html) for NetBox Ansible collection is used to dynamically generate the inventory from NetBox to be used in the Ansible playbook:

In the `ansible.cfg` file we are specifying that the inventory should be sourced from the file `netbox_inv.yml`:

 ```
 # ansible.cfg

 [defaults]
 inventory = ./netbox_inv.yml
 ```

The plugin is highly configurable in terms of defining returned hosts and groupings etc in the inventory, so please consult the [docs](https://docs.ansible.com/ansible/latest/collections/netbox/netbox/nb_inventory_inventory.html).

In this case we are grouping the returned hosts by the `device_roles` and `sites` as defined in the NetBox data model:

```
 # netbox_inv.yml

 plugin: netbox.netbox.nb_inventory
 validate_certs: False
 group_by:
  - device_roles
  - sites
```


To view a graph of the inventory retrieved from NetBox, you can run the `ansible-inventory` command and specify the `netbox_inv.yml` file as the source, followed by `--graph:

```
ansible-inventory -i netbox_inv.yml --graph
```

From the returned output we can see that our NetBox instance has returned the data expected nd we have a few `device_roles` and `sites`:

@all:
  |--@device_roles_access:
  |  |--sw3
  |  |--sw4
  |--@device_roles_access_switch:
  |  |--SWITCH-1
  |--@device_roles_distribution:
  |  |--sw1
  |  |--sw2
  |--@device_roles_security_appliance:
  |  |--SEC-APP-1
  |--@device_roles_wireless_ap:
  |  |--AP-1
  |--@sites_cisco_devnet:
  |  |--sw1
  |  |--sw2
  |  |--sw3
  |  |--sw4
  |--@sites_meraki_sandbox:
  |  |--AP-1
  |  |--SEC-APP-1
  |  |--SWITCH-1
  |--@ungrouped:

To list all the devices in the inventory, use the same command, but with the `--list` suffix:
```
ansible-inventory -i netbox_inv.yml --list
```



1. The Ansible playbooks target hosts based on the `device_roles` as defined in NetBox and pulled from the dynamic inventory. They contain a `set_facts` task to map the values of the `ccc_device_id` and `cisco_catalyst_center` custom fields to the devices, so they can be used in later tasks per inventory device:

    ```
    ---
    - name: Get Device Details From Cisco Catalyst Center
      hosts: device_roles_distribution, device_roles_access
    ```

    ```
    tasks:
        - name: Set Custom Fields as Facts for Cisco Catalyst Center host and Device UUID
        set_fact:
            cisco_catalyst_center: "{{ hostvars[inventory_hostname].custom_fields['cisco_catalyst_center'] }}"
            ccc_device_id: "{{ hostvars[inventory_hostname].custom_fields['ccc_device_id'] }}"
    ```

    ```
    - name: Get Device Details
      uri:
        url: "https://{{ cisco_catalyst_center }}/dna/intent/api/v1/network-device/{{ ccc_device_id }}"
        method: GET
        return_content: yes
        validate_certs: no
        headers:
          Content-Type: "application/json"
          x-auth-token: "{{ login_response.json['Token'] }}"
      register: device_details
      delegate_to: localhost
    ```

## Getting Started with the Ansible Playbooks

1. Clone the Git repo and change into the `netbox-ansible-cisco-cc` directory:
    ```
    git clone https://github.com/netboxlabs/netbox-learning.git
    cd netbox-learning/netbox-ansible-cisco-cc
    ```
2. Create and activate Python 3 virtual environment:
    ```
    python3 -m venv ./venv
    source venv/bin/activate
    ```
3. Install required Python packages:
    ```
    pip install -r requirements.txt
    ```
4. Set environment variables for the NetBox API token and URL:
    ```
    export NETBOX_API=<YOUR_NETBOX_URL> (note - must include http:// or https://)
    export NETBOX_TOKEN=<YOUR_NETBOX_API_TOKEN>
    ```
5. List the devices and host variables retrieved from NetBox using the dynamic inventory:
    ```
    ansible-inventory -i netbox_inv.yml --list
    ```
6. Note how the Custom Fields `ccc_device_id` and `cisco_catalyst_center` and their values are retrieved for each device:
    ```
    "sw4": {
        "ansible_host": "10.10.20.178",
        "custom_fields": {
            "ccc_device_id": "826bc2f3-bf3f-465b-ad2e-e5701ff7a46c",
            "cisco_catalyst_center": "sandboxdnac.cisco.com"
        },
    ```
7. Run a playbook making sure to specify the NetBox dynamic inventory with the `-i` flag. For example:
    ```
    ansible-playbook -i netbox_inv.yml get_device_details.yml
    ```
8. When you have finished working you can deactivate the Python virtual environment:
    ```
    deactivate
    ```

## References
- [NetBox Offical Docs](https://docs.netbox.dev/en/stable/)
- [NetBox Inventory Plugin for Ansible](https://docs.ansible.com/ansible/latest/collections/netbox/netbox/nb_inventory_inventory.html)
- [Cisco Catalyst Center API Docs](https://developer.cisco.com/docs/dna-center/2-3-7/)
