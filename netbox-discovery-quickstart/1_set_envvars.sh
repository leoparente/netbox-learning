#!/bin/bash

# Attempt to fetch the external IPv4 address
EXTERNAL_IP=$(curl -4 -s ifconfig.me)  # Use -4 to ensure IPv4 is returned

# Check if the IP was retrieved successfully
if [ -z "$EXTERNAL_IP" ]; then
  echo "Error: Unable to determine external IPv4 address."
  exit 1
fi

export MY_EXTERNAL_IP=$EXTERNAL_IP

# NetBox port
export NETBOX_PORT="8000"

# Subnet for the Docker network to run all the services in
export DOCKER_SUBNET="172.24.0.0/24"
export DOCKER_NETWORK="discovery-quickstart"

# API key for the Diode service to interact with NetBox
export DIODE_TO_NETBOX_API_KEY=$(head -c20 </dev/urandom|xxd -p)

# API key for the NetBox service to interact with Diode
export NETBOX_TO_DIODE_API_KEY=$(head -c20 </dev/urandom|xxd -p)

# API key for Diode SDKs to ingest data into Diode
export DIODE_API_KEY=$(head -c20 </dev/urandom|xxd -p)

#  API key to authorize RPC calls between the Ingester and Reconciler services
export INGESTER_TO_RECONCILER_API_KEY=$(openssl rand -base64 40 | head -c 40)


# Debug information to communicate values being used
echo
echo "--- Environment Variables Set ---"
echo "External IP: $MY_EXTERNAL_IP"
echo "NetBox will be deployed at: http://$MY_EXTERNAL_IP:$NETBOX_PORT"
echo "Docker subnet: $DOCKER_SUBNET"
echo "Docker network: $DOCKER_NETWORK"
echo DIODE_TO_NETBOX_API_KEY: ${DIODE_TO_NETBOX_API_KEY}
echo NETBOX_TO_DIODE_API_KEY: ${NETBOX_TO_DIODE_API_KEY}
echo DIODE_API_KEY: ${DIODE_API_KEY}
echo INGESTER_TO_RECONCILER_API_KEY: ${INGESTER_TO_RECONCILER_API_KEY}
echo "-----------------------------------"