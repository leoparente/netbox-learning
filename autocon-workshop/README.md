# NetBox Config Pusher for AutoCon Workshop

## Requirements

- docker
- docker-compose

## Configuration

- NetBox Cloud credentials go in `docker-compose.yml`
- The rest can stay the same if using the preconfigured workshop clab lab
- `networks` must contain the same `docker network` that is used for the clab lab. This is hard coded to work in the workshop, but if you're curious you can inspect using 'docker network ls`

## Usage

Normal usage: `docker-compose up`
If you've made changes to the code: `docker-compose up --build`

## Behaviour

- Pulls device information (Name, IP, Platform) from NetBox for the device names specified on the command line ("fiber" and "plane") by default
- Generates the configurations for the devices using NetBox's `/render-config/` endpoint
- Connects to the devices
- Pushes the generated configs
- Pulls the config and reports any differences