# filename: generate_testbed_file.py

# Description: This script generates a testbed file based on the Netbox data
#              using the pyATS framework. It uses the Netbox class from the
#              pyats.contrib.creators.netbox module to create the testbed file.

# Import the necessary libraries
from pyats.contrib.creators.netbox import Netbox
import yaml
import os

# Define Netbox URL, user token, and default credentials
netbox_url = os.getenv('NETBOX_URL')
user_token = os.getenv('NETBOX_USER_TOKEN')
def_user = '%ENV{DEF_PYATS_USER}'
def_pass = '%ENV{DEF_PYATS_PASS}'
url_filter = 'site=pyats-webinar'
# url_filter = 'site_id=68'
# url_filter = 'site=pyats-webinar&os=ios-xe'
# url_filter = 'platform=ios-xe'

# Create testbed object and build data structure
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