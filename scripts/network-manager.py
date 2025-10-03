#!/usr/bin/env python3
# network-manager.py
# Author: Luxforge
# This module is responsible for managing Docker networks based on environment variable configurations.


import subprocess                     # For running Docker CLI commands
from pathlib import Path              # For filesystem navigation and path handling
from dotenv import dotenv_values      # For loading .env files as dictionaries

# Default fallback values if .env files are missing keys
DEFAULTS = {
    "SUBNET": "192.168.99.0/24",
    "GATEWAY": "192.168.99.1",
    "PARENT_IF": "eth0",
    "DRIVER": "macvlan",
    "NETWORK_NAME": "default-network"
}

class NetworkManager:
    def __init__(self, env_dir="./config/networks", log_file="./create-networks.log"):
        # Initialize paths for central config and optional logging
        self.env_dir = Path(env_dir)
        self.log_file = Path(log_file)

        # Load central environment variables if logs.env exists
        central_env_path = self.env_dir / "logs.env"
        self.central_env = dotenv_values(central_env_path) if central_env_path.exists() else {}

    def scan_env_files(self, root="."):
        # Recursively find all .env files starting from the given root
        return list(Path(root).rglob(".env"))

    def load_env(self, env_file):
        # Load variables from the given .env file
        env_vars = dotenv_values(env_file)

        # Merge defaults, central config, and local .env values (local overrides central)
        return {**DEFAULTS, **self.central_env, **env_vars}

    def network_exists(self, name):
        # Check if a Docker network with the given name already exists
        result = subprocess.run(["docker", "network", "ls"], capture_output=True, text=True)
        return name in result.stdout

    def create_network(self, config):
        # Build the Docker network create command using config values
        cmd = [
            "docker", "network", "create",
            "-d", config["DRIVER"],
            "--subnet", config["SUBNET"],
            "--gateway", config["GATEWAY"],
            "-o", f"parent={config['PARENT_IF']}",
            config["NETWORK_NAME"]
        ]

        # Run the command and return True if successful
        return subprocess.run(cmd).returncode == 0

    def process_env_file(self, env_file):
        print(f"[INFO] Processing {env_file}")

        # Load and merge environment variables
        config = self.load_env(env_file)

        # Ensure all required fields are present
        required = ["NETWORK_NAME", "SUBNET", "GATEWAY", "PARENT_IF"]
        if not all(config.get(k) for k in required):
            print(f"[WARN] Missing required variables in {env_file}. Skipping.")
            return

        # Skip creation if the network already exists
        if self.network_exists(config["NETWORK_NAME"]):
            print(f"[INFO] Network '{config['NETWORK_NAME']}' already exists. Skipping creation.")
            return

        # Attempt to create the network
        print(f"[INFO] Creating network '{config['NETWORK_NAME']}' from {env_file}...")
        if self.create_network(config):
            print(f"[SUCCESS] Network '{config['NETWORK_NAME']}' created.")
        else:
            print(f"[ERROR] Failed to create network '{config['NETWORK_NAME']}'.")

    def batch_create(self):
        # Process all discovered .env files
        for env_file in self.scan_env_files():
            self.process_env_file(env_file)