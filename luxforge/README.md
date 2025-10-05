# Quinly Management VLAN Setup

This script creates a Docker macvlan network for internal service communication.

## Usage

```bash
NETWORK_NAME=quinly-management \
SUBNET=192.168.99.0/24 \
GATEWAY=192.168.99.1 \
PARENT_IF=eth0 \
./create-quinly-management.sh
```