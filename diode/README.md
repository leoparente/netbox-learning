# Diode

Diode is a NetBox data ingestion service that greatly simplifies and enhances the process to add and update network data in NetBox, ensuring your network source of truth is always accurate and can be trusted to power your network automation pipelines. Our guiding principle in designing Diode has been to make it as easy as possible to get data into NetBox, removing as much burden as possible from the user while shifting that effort to technology.

See the main [Diode project](https://github.com/netboxlabs/diode) page to find more details and additional resources.

## Diode SDK Python

To use the examples in this repository, you'll need to install the Diode SDK.

### Set Up and Installation

Pre-requisites:

* Python >= 3.10

1. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Upgrade pip:

```
python3 -m pip install --upgrade pip
```

3. Install the Diode SDK:

```bash
pip install netboxlabs-diode-sdk
```

4. Set the following environment variables:

```bash
export DIODE_API_KEY=<generated when configuring your Diode plugin>
```

### Example scripts

All scripts have an optional flags:

```
--target TARGET  the target address of the Diode server (default: grpc://localhost:8081)
--apply          apply the changes (default: False)
```

#### CSV data ingestion

Parses a CSV file and extracts information about the device and ingests it into NetBox using the Diode SDK.

```bash
python3 examples/csv/main.py [--target TARGET] [--apply]
```

#### Containerlab

Parses a Containerlab configuration file and extracts information about the device and its interfaces, including IP
addresses and ingests it into NetBox using the Diode SDK.

```bash
python3 examples/containerlab/main.py [--target TARGET] [--apply]
```

#### Cisco IOS

Parses Cisco IOS configuration file and extracts information about the device and its interfaces, including IP addresses
and ingests it into NetBox using the Diode SDK.

Requires additional dependencies:

```bash
pip install ciscoconfparse2
```

```bash
python3 examples/cisco_ios/main.py [--target TARGET] [--apply]
```
