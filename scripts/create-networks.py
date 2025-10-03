#!/usr/bin/env python3

# Management VLAN Batch Setup
# Author: Luxforge

import os
import subprocess
from pathlib import Path
from dotenv import dotenv_values


ENV_DIR = Path("./config/networks")
LOG_FILE = Path("./create-networks.log")

# Load central config if available
central_env = dotenv_values(ENV_DIR / "logs.env")

# Scan for all .env files
env_files = list(Path(".").rglob(".env"))

for env_file in env_files:
    print(f"[INFO] Processing {env_file}")

    # Load variables from .env file
    env_vars = dotenv_values(env_file)
    env = {**DEFAULTS, **central_env, **env_vars}

    # Validate required fields
    required = ["NETWORK_NAME", "SUBNET", "GATEWAY", "PARENT_IF"]
    if not all(env.get(k) for k in required):
        print(f"[WARN] Missing required variables in {env_file}. Skipping.")
        continue

    network_name = env["NETWORK_NAME"]

    # Check if network already exists
    result = subprocess.run(
        ["docker", "network", "ls"],
        capture_output=True, text=True
    )
    if network_name in result.stdout:
        print(f"[INFO] Network '{network_name}' already exists. Skipping creation.")
        continue

    # Create the network
    print(f"[INFO] Creating network '{network_name}' from {env_file}...")
    create_cmd = [
        "docker", "network", "create",
        "-d", env["DRIVER"],
        "--subnet", env["SUBNET"],
        "--gateway", env["GATEWAY"],
        "-o", f"parent={env['PARENT_IF']}",
        network_name
    ]
    create_result = subprocess.run(create_cmd)

    if create_result.returncode == 0:
        print(f"[SUCCESS] Network '{network_name}' created.")
    else:
        print(f"[ERROR] Failed to create network '{network_name}'.")