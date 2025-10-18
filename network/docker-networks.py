#! /usr/bin/env python3

# network/docker-networks.py
# Script to create Docker networks based on environment variables.

import os
import docker
from dotenv import dotenv_values
from dotenv import load_dotenv
from pathlib import Path

def create_macvlan_network(name, subnet, gateway, parent_if):
    ipam_pool = docker.types.IPAMPool(
        subnet=subnet,
        gateway=gateway
    )
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
    client = docker.from_env()
    existing = [net.name for net in client.networks.list()]

    if name in existing:
        print(f"[-] Skipping {name}: already exists")
        return

    try:
        client.networks.create(
            name=name,
            driver="macvlan",
            options={"parent": parent_if},
            ipam=ipam_config
        )
        print(f"[✓] Created macvlan network: {name}")
    except docker.errors.APIError as e:
        print(f"[!] Failed to create {name}: {e.explanation}")

def main():
    # Load environment variables from .env file - in this dir
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("[!] .env file not found.")
        return
    load_dotenv()
    config = dotenv_values(env_file)
    # Print loaded environment variables
    print("[*] Loaded environment variables:")
    for key, value in config.items():
        print(f"    {key}={value}")
    prefixes = ["IOT", "MANAGEMENT", "SERVICES"]

    for prefix in prefixes:
        name = config.get(f"{prefix}_NETWORK_NAME")
        subnet = config.get(f"{prefix}_SUBNET")
        gateway = config.get(f"{prefix}_DEFAULT_GATEWAY")
        parent_if = config.get(f"{prefix}_PARENT_IF")
        driver = config.get(f"{prefix}_DRIVER")

        if driver != "macvlan":
            print(f"[!] Skipping {name}: unsupported driver '{driver}'")
            continue

        if all([name, subnet, gateway, parent_if]):
            create_macvlan_network(name, subnet, gateway, parent_if)
        else:
            print(f"[!] Incomplete config for {prefix}, skipping.")

if __name__ == "__main__":
    main()