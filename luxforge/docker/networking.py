#!/usr/bin/env python3

# Generate networks based on env files for Docker
# Author: Luxforge

import os
import subprocess
from utils.logger import logger
from menu import Menu
from utils.colours import Colours

class NetworkProfile:
    """
    Create Docker networks based on environment variables.
    Environment variables should be prefixed with the network type, e.g., IOT_, MANAGEMENT_, SERVICES_.
    """
    REQUIRED_KEYS = [
        "NETWORK_NAME",
        "SUBNET",
        "DEFAULT_GATEWAY",
        "PARENT_IF",
        "DRIVER"
    ]
 
    def __init__(self, ):
        # Need to load env_profile first to get env vars
        from utils.envprofile import env_profile

        # Store the provided prefixes and initialize networks dictionary
        # Log the prefixes being used
        self.prefixes = self.discover_prefixes()
        logger.d(f"Initializing NetworkProfile with prefixes: {self.prefixes}")
        self.networks = {}

        # Load all network configs
        for prefix in self.prefixes:
            self.networks[prefix] = self._load_config(prefix)

    def _load_config(self, prefix: str) -> dict:
        """
        Load the network configuration for a specific prefix.
        ARGS:
            prefix (str): The network prefix (e.g., "IOT", "MANAGEMENT", "SERVICES")
        RETURNS:
            dict: The network configuration
        """
        config = {}
        for key in self.REQUIRED_KEYS:
            full_key = f"{prefix}_{key}"
            config[key] = self.get_env_strict(full_key)
        return config

    def get_env_strict(self, key: str) -> str:
        """
        Fetch an environment variable and raise an error if it's missing or empty
        ARGS:
            key (str): The base key name (e.g., "SUBNET")
        RETURNS:
            str: The value of the environment variable
        RAISES:
            RuntimeError: If the environment variable is missing or empty
        """
        # Validate inputs
        if not key:
            logger.critical("Key must be provided to get_env_strict")
            exit(1)
        
        # Try to get the environment variable
        try:
            value = os.getenv(key)
        except Exception as e:
            logger.critical(f"Error retrieving environment variable {key}: {e}")
            exit(1)
        
        # Check if the value is missing or empty
        if value is None or value.strip() == "":
            logger.critical(f"Missing required environment variable: {key}")
            exit(1)
        
        # Good stuff - show debug info and return the value
        logger.d(f"Retrieved env key:{key} = {value}")

        # Return the stripped value
        return value.strip()

    def network_exists(self, name: str) -> bool:
        # Check if a Docker network with the given name already exists
        # validate input
        if not name:
            logger.error("Network name must be provided to check existence")
            return False

        # Clean the name
        name = name.strip().lower()

        logger.d(f"Checking if Docker network '{name}' exists...")
        
        # Use subprocess to call `docker network inspect`
        result = subprocess.run(
            f"docker network inspect {name}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        exists = result.returncode == 0
        if exists:
            logger.info(f"Docker network '{name}' already exists.")
        else:
            logger.info(f"Docker network '{name}' does not exist.")
        return exists

    def create_network(self, prefix: str):
        """
        Create a Docker network based on environment variables.
        ARGS:
            prefix (str): The network prefix (e.g., "IOT", "MANAGEMENT", "SERVICES")
        RAISES:
            RuntimeError: If required environment variables are missing
        RETURNS:
            None
        """
        
        # Fetch and validate all required environment variables
        logger.i(f"Preparing Docker network for prefix: {prefix}")
        config = {}

        # Fetch each required key with strict validation and place them into config
        for key in self.REQUIRED_KEYS:
            full_key = f"{prefix}_{key}"
            config[key] = self.get_env_strict(full_key)

        # Build the docker network create command
        cmd = (
            f"docker network create -d {config['DRIVER']} "
            f"--subnet={config['SUBNET']} --gateway={config['DEFAULT_GATEWAY']} "
            f"-o parent={config['PARENT_IF']} {config['NETWORK_NAME']}"
        )

        # Check if the network already exists
        if self.network_exists(config["NETWORK_NAME"]):
            return

        # Check if the parent interface is up
        if not self.interface_up(config["PARENT_IF"]):
            error_msg = f"Parent interface '{config['PARENT_IF']}' is not up. Cannot create network '{config['NETWORK_NAME']}'."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Check for subnet conflicts
        if self.subnet_conflict(config["SUBNET"]):
            logger.error(f"Subnet conflict detected: {config['SUBNET']} already in use. Skipping '{prefix}'")
            return

        # Log as info and attempt to create the network
        logger.info(f"Creating Docker network: {prefix}")
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip()
            logger.error(f"Failed to create Docker network '{config['NETWORK_NAME']}': {error_msg}")
            raise RuntimeError(error_msg)
        else:
            logger.changelog(
                f"Docker network '{config['NETWORK_NAME']}' created successfully. "
                f"Using subnet {config['SUBNET']} via {config['PARENT_IF']}"
            )

    def create_networks(self):
        for prefix in self.prefixes:
            config = self.networks[prefix]
            if self.confirm_action(prefix, config):
                try:
                    self.create_network(prefix)
                except RuntimeError as e:
                    logger.error(f"Skipping network '{prefix}' due to error: {e}")
            else:
                logger.warn(f"Skipped network '{prefix}' by user choice.")
            

    def discover_prefixes(self) -> list[str]:
        # Discover all unique network prefixes from environment variables
        prefixes = set()
        for key in os.environ:
            if key.endswith("_NETWORK_NAME"):
                prefix = key.split("_NETWORK_NAME")[0]
                if prefix:
                    prefixes.add(prefix.upper())
        return sorted(prefixes)
    
    def interface_up(self, iface: str) -> bool:
        # Check if a network interface is up
        result = subprocess.run(f"ip link show {iface}", shell=True, capture_output=True, text=True)
        return "state UP" in result.stdout

    def subnet_conflict(self, subnet: str) -> bool:
        # Check if the given subnet conflicts with existing Docker networks
        result = subprocess.run(
            "docker network inspect $(docker network ls -q)",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.warn("Unable to inspect existing Docker networks for subnet conflict check.")
            return False

        return subnet in result.stdout

    def confirm_action(self, prefix: str, config: dict) -> bool:
        print(f"\n[CONFIRM] Network: {config['NETWORK_NAME']}")
        print(f"  Subnet: {config['SUBNET']}")
        print(f"  Gateway: {config['DEFAULT_GATEWAY']}")
        print(f"  Parent Interface: {config['PARENT_IF']}")
        print(f"  Driver: {config['DRIVER']}")
        choice = input(f"Create network '{prefix}'? [y/N]: ").strip().lower()
        return choice == "y"

class DockerNetworkMenu(Menu):
    """
    Interactive CLI menu for Docker network profile management tasks.
    """
    options = {
        "1": ("View Network Profiles", "view_profiles"),
        "2": ("See Current Networks", "show_docker_networks"),
        "C": ("Create Networks", "create_networks"),
    }
    menu_name = "Docker Network Menu"

    def create_networks(self):
        self._show_menu(self.create_networks_options)

    def view_profiles(self):
        """
        View Docker network profiles. 
        """

        # Check if any profiles exist
        if not network_profile.networks:
            print("\nNo network profiles found.")
            input("\nPress Enter to return to the menu...")
            return
        
        # Check if any of the profiles are incomplete
        incomplete_profiles = []
        for prefix, config in network_profile.networks.items():
            missing_keys = [key for key in NetworkProfile.REQUIRED_KEYS if key not in config or not config[key]]
            if missing_keys:
                incomplete_profiles.append((prefix, missing_keys))
        if incomplete_profiles:
            print("\n[WARNING] Incomplete network profiles detected:")
            for prefix, missing in incomplete_profiles:
                print(f"  Profile '{prefix}' is missing keys: {', '.join(missing)}")
            print("Please check your environment variables.")
            input("\nPress Enter to return to the menu...")
            return

        # If a profile is in use, identify it
        in_use_profiles = []
        free_profiles = []
        for network in network_profile.networks.items():
            if network_profile.network_exists(network[0]):
                in_use_profiles.append(network)
                logger.d(f"Network profile '{network[0]}' is currently in use.")
            else:
                free_profiles.append(network)
                logger.d(f"Network profile '{network[0]}' is free to use.")             

        print("\n[Network Profiles]")
        for prefix, config in network_profile.networks.items():

            # Highlight if in use or free
            if prefix in [p[0] for p in in_use_profiles]:
                status = Colours.colour_text(" (In Use)", "ORANGE", bold=True)
            else:
                status = Colours.colour_text(" (Free)", "GREEN", bold=True)
            print(f"\nProfile: {prefix} -- " + status)
            for key, value in config.items():
                print(f"  {key}: {value}")

        input("\nPress Enter to return to the menu...")

    def show_docker_networks(self):
        print("\n[Current Docker Networks]")
        subprocess.run("docker network ls", shell=True)
        input("\nPress Enter to return to the menu...")


network_profile = NetworkProfile()

if __name__ == "__main__":  
    from luxforge.utils.logger import logger
    docker_menu = DockerNetworkMenu()
    docker_menu.launch()