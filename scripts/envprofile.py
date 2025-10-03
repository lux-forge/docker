# envprofile.py
# Author: Luxforge
# Modular environment loader for node-specific .env files

import os
from pathlib import Path
from dotenv import dotenv_values
from files import find_all_files
import socket
from luxforge_logger import luxforgeLogger


class EnvProfile:
    """
    Load and merge .env files from global and node-specific directories.
    ARGS:
        config_root: Root directory for config files (default: "config")
    METHODS:
        
    PROPERTIES:
        config: Merged configuration dictionary
    """

    def __init__(
            self, 
            config_root: str ="./config"
        ):
        # Initialize paths and load .env files
        
        # Set root config directory and node name
        self.config_root = Path(config_root).resolve()
        
        # Set the node name - either override or auto-detect
        self.node = socket.gethostname()
        self.node_name = self.node.upper()

        # Load defaults
        print(f"[INFO] Loading EnvProfile for node '{self.node_name}' from '{self.config_root}'")
        self._load_defaults()

        # Load global and node-specific .env files
        node_env_files = find_all_files(self.config_root / "nodes" / self.node_name, "*.env")
        global_env_files = find_all_files(self.config_root / "global", "*.env")

        # Merge all .env files, with node-specific taking precedence over global
        env_files = global_env_files + node_env_files
        self.loaded_keys = {}

        # Load and merge all .env files in order
        for env_file in env_files:
            luxforgeLogger.info(f"Loaded .env file: {env_file}")
            values = dotenv_values(env_file)

            # Log loaded keys
            for k, v in values.items():
                self.inject_into_os_env(k, v)

    def _load_defaults(self) -> None:
        # Load default values from defaults.env
        
        defaults_path = self.config_root / "EXAMPLE" / "global" / "networks" / "defaults.env"
        luxforgeLogger.d(f"Loading default environment variables from defaults: {defaults_path}")
        if defaults_path.exists():
            self.defaults = dotenv_values(defaults_path)
            return
        
        # Fallback hardcoded defaults
        self.defaults = dotenv_values(self.defaults) if self.defaults.exists() else {
            "SUBNET": "192.168.99.0/24",
            "GATEWAY": "192.168.99.1",
            "PARENT_IF": "eth0",
            "DRIVER": "macvlan",
            "NETWORK_NAME": "default-network"
        }
    def preview(self):
        # Return merged config as printable string
        return "\n".join(f"{k} = {v}" for k, v in self.loaded_keys.items())

    def as_dict(self):
        return dict(self.loaded_keys)

    def inject_into_os_env(self, key: str, value: str) -> None:
        # See if key already exists and log override
        key = key.upper()
        if key in os.environ:
            luxforgeLogger.warn(f"Overriding os.environ[{key}]: {os.environ[key]} → {value}")
            
       
        # Inject loaded keys into os.environ for global access
        os.environ[key] = value
        luxforgeLogger.i(f"Set os.environ[{key}] = {value}")

# Generate a global instance for easy access
env_profile = EnvProfile()