# netbox-pyats-webinar

Code to accompany the **Webinar: Getting Started with Network Test Automation: NetBox + pyATS +** hosted by **NetBox Labs** on 23rd April 2024.

[![netbox pyats webinar](https://fixme.jpg)](https://www.youtube.com/watch?fixme)

## Get Access to a NetBox instance

For hassle-free access to NetBox you can either use the NetBox Labs demo site, or request a free 14 Day Trial of NetBox Cloud: 

- [Demo Site](https://netboxlabs.com/netbox-demo/)
- [Free Trial of NetBox Cloud](https://netboxlabs.com/trial/)

## Getting Started With NetBox, PyATS and Genie

### Set Up and Installation

1. Clone the Git repo and change into the `netbox-pyats-webinar` directory:
    ```
    git clone https://github.com/netboxlabs/netbox-learning.git
    cd netbox-learning/netbox-pyats-webinar
    ```
2. Create and activate Python 3 virtual environment:
    ```
    python3 -m venv ./venv
    source venv/bin/activate
    ```
3. Upgrade pip:
    ```
    python3 -m pip install --upgrade pip
    ```
4. Install PyATS:

    **Option 1**
    Minimal install that includes the Genie library and that allows you to use the interactive testbed creation command to create your testbed files from NetBox: 
    ```
    pip install pyats[library]
    pip install pyats.contrib
    ```

    **Option 2**
    Full installation that includes all packages and libraries: 
    ```
    pip install pyats[full]
    ```

    *Note* If you are using Zsh on a Mac then you need to quote the install string (this had me stuck for a long time until I figured it out!)
    ```
    pip install "pyats[full]"
    ```
    
    **Option 3**
    Run the [PyATS Docker Image](https://developer.cisco.com/codeexchange/github/repo/CiscoTestAutomation/pyats-docker). This command will pull down the container if you don't have it locally and drop you into a Bash shell: 
    ```
    docker run -it ciscotestautomation/pyats:latest /bin/bash
    ```

## Lab Network

blah, blah, diagram....


### Generating The testbed file Dynamically from NetBox Inventory

**Option 1**
Use the `pyats create testbed netbox` command to build your testbed file. Note that where a value is prefixed with `os.getenv` or `%ENV` then these values are being pulled in from the local environment variables that you set with the `export` command eg. `export NETBOX_URL=https://example.cloud.netboxapp.com/`:
```
pyats create testbed netbox \
--output webinar-cisco-testbed.yaml \
--netbox-url=${NETBOX_URL} \
--user-token=${NETBOX_USER_TOKEN} \
--def_user='%ENV{DEF_PYATS_USER}' \
--def_pass='%ENV{DEF_PYATS_PASS}' \
--url_filter='site=pyats-webinar' \
--topology
```

In this example we are generating a testbed file called `webinar-cisco-testbed.yaml` and filtering NetBox by the site name `pyats-webinar`. When you hit enter the output will look like this: 

```
Begin retrieving data from netbox...
Configuring testbed default credentials.
Retrieving associated data for CSR1...
Retrieving associated data for CSR2...
Testbed file generated: 
webinar-cisco-testbed.yaml 
```
**Option 2**
Run the `generate_testbed_file.py` Python script. Note that where a value is prefixed with `os.getenv` or `%ENV` then these values are being pulled in from the local environment variables contained in the `.env` file. To use this you should rename the file `.env.example` to `.env` and replace the values with those for your own environment. 

In this script we are generating a testbed file called `testbed.yaml` and filtering NetBox by the site name `pyats-webinar`, but you could just as easily filter on other fields as in the examples commented out: 

```
from pyats.contrib.creators.netbox import Netbox
from dotenv import load_dotenv
import yaml
import os

# Load environment variables
load_dotenv()

# Get environment variables from .env file and set url_filter
netbox_url = os.getenv('NETBOX_URL')
user_token = os.getenv('NETBOX_USER_TOKEN')
def_user = '%ENV{DEF_PYATS_USER}'
def_pass = '%ENV{DEF_PYATS_PASS}'
url_filter = 'site=pyats-webinar'
# url_filter = 'site_id=68'
# url_filter = 'site=pyats-webinar&os=ios-xe'
# url_filter = 'platform=ios-xe'

# Create Netbox object and build testbed data structure
nb_testbed = Netbox(
    netbox_url=netbox_url,
    user_token=user_token,
    def_user=def_user,
    def_pass=def_pass,
    url_filter=url_filter,
    ssl_verify=False,
    topology=True
)

# Generate testbed file
tb = nb_testbed._generate()
tb_yaml = yaml.dump(tb)
with open("testbed.yaml", "w") as f:
    f.write(tb_yaml)
```
The resulting testbed file produced by either option will look something like this, depending on your network. Note that as we included the `--topology` switch the testbed file output includes the interfaces and connections from NetBox also: 
```
devices:
  CSR1:
    alias: CSR1
    connections:
      cli:
        ip: 10.90.0.35
        protocol: ssh
    credentials:
      default:
        password: '%ENV{DEF_PYATS_PASS}'
        username: '%ENV{DEF_PYATS_USER}'
    os: iosxe
    platform: iosxe
    type: CSR1000V
  CSR2:
    alias: CSR2
    connections:
      cli:
        ip: 10.90.0.36
        protocol: ssh
    credentials:
      default:
        password: '%ENV{DEF_PYATS_PASS}'
        username: '%ENV{DEF_PYATS_USER}'
    os: iosxe
    platform: iosxe
    type: CSR1000V
testbed:
  credentials:
    default:
      password: '%ENV{DEF_PYATS_PASS}'
      username: '%ENV{DEF_PYATS_USER}'
topology:
  CSR1:
    interfaces:
      GigabitEthernet1:
        alias: CSR1_GigabitEthernet1
        ipv4: 10.90.0.35/27
        type: ethernet
      GigabitEthernet2:
        alias: CSR1_GigabitEthernet2
        ipv4: 192.168.1.1/30
        link: cable_num_34
        type: ethernet
      GigabitEthernet3:
        alias: CSR1_GigabitEthernet3
        type: ethernet
      GigabitEthernet4:
        alias: CSR1_GigabitEthernet4
        type: ethernet
      GigabitEthernet5:
        alias: CSR1_GigabitEthernet5
        type: ethernet
  CSR2:
    interfaces:
      GigabitEthernet1:
        alias: CSR2_GigabitEthernet1
        ipv4: 10.90.0.36/27
        type: ethernet
      GigabitEthernet2:
        alias: CSR2_GigabitEthernet2
        ipv4: 192.168.1.2/30
        link: cable_num_34
        type: ethernet
      GigabitEthernet3:
        alias: CSR2_GigabitEthernet3
        type: ethernet
      GigabitEthernet4:
        alias: CSR2_GigabitEthernet4
        type: ethernet
      GigabitEthernet5:
        alias: CSR2_GigabitEthernet5
        type: ethernet
```