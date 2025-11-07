# /#!/usr/bin/env python3

# users.py
# Author: Luxforge
# User management for Luxforge tools and docker containers

import yaml
from pathlib import Path
from userGenerator import UserGenerator 
from foundry.logger import Logger

logger = Logger("UserProvisioner")

class UserProvisioner:
    """
    User provisioner that reads a YAML config and provisions users accordingly.
    """
    
    def __init__(self, config_path: str = "users.yaml"):

        # Load and parse the YAML config
        self.config_path = Path(config_path)
        self.raw_config = self.load_yaml()

        # Dynamically retrieve sections with user definitions - ignore example section
        self.sections = {}
        self.apply_sections()
        self.users = ()

        self.results = []

    def load_yaml(self):
        if not self.config_path.exists():
            logger.error(f"User config file not found: {self.config_path}")
            raise FileNotFoundError(f"User config file not found: {self.config_path}")
        
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def apply_sections(self):
        """
        Apply user sections from the raw config.
        """
        for section_name, section_data in self.raw_config.items():
            if section_name.lower() == "example":
                continue  # Skip global defaults
            
            logger.debug(f"Applying section: {section_name}")
            self.sections[section_name] = section_data

    def merge_config(self, section_config: dict, user_config: dict):
        merged = {}
        merged.update(section_config)
        merged.update(user_config)

        # Assign UID if missing
        if "uid" not in merged:
            merged["uid"] = None # userGenerator will assign next available

        # Assign GID: match UID if not explicitly set
        if "gid" not in merged:
            merged["gid"] = merged["uid"]

        return merged

    def prepare_user(self , user_config: dict, section_config: dict, name: str = ""):
        """
        Provision a single user based on the provided config.
        PARAMS:
            user: dict - The user configuration to provision.
            section_defaults: dict - The default values from the section.
        """
        
        # The name is the key to the user dictionary        
        user_config["name"] = f"{name}"
        prepared_config = self.merge_config(section_config, user_config)

        # Append to users list for UserGenerator
        self.users.append(prepared_config)
        logger.info(f"Prepared user '{name}'. UID={prepared_config.get('uid', 'N/A')}. GID={prepared_config.get('gid', 'N/A')}.")

    def provision_section(self, section_name: str):
        """
        Provision all users in a given section.
        PARAMS:
            section_name: str - The name of the section to provision.
        """

        if section_name not in self.sections.keys():
            logger.error(f"Section '{section_name}' not found in config.")
            raise ValueError(f"Section '{section_name}' not found in config.")

        # Clear users list for this section
        self.users = []

        # Get section data and defaults
        section_users = self.sections[section_name].get("users", [])
        section_defaults = self.sections[section_name].get("default", [])

        logger.info(f"🚀 Provisioning section '{section_name}'. Total Users: {len(section_users)}")
        for user_name, user_config in section_users.items():
            self.prepare_user(user_config=user_config, section_config=section_defaults, name=user_name)
        
        # Now provision all users collected in self.users
        for user_config in self.users:
            self.provision_user(user_config=user_config)
            self.brief_review()
        logger.info(f"✅ Completed provisioning section '{section_name}'.")

    def provision_user(self, user_config: dict):
        """
        Provision a single user from a given section.
        PARAMS:
            user_config: dict - The user configuration to provision.
        """
        try:
            ug = UserGenerator(config=user_config)
            artifact = ug.emit_artifact()
            logger.info(f"✅ Provisioned '{user_config['name']}' with UID {artifact['uid']} and groups {artifact['groups']}")
            self.results.append({"name": user_config['name'], "status": "PASS", "artifact": artifact})
        except Exception as e:
            logger.error(f"❌ Failed to provision '{user_config['name']}': {e}")
            self.results.append({"name": user_config['name'], "status": "FAIL", "error": str(e)})

    def provision_all(self):
        for section_name in self.sections:
            self.provision_section(section_name)
        logger.info("🚀 Completed provisioning all sections.")
    
    def brief_review(self):
        """
        Provide a brief of the logged results.
        """
        print("User Provisioning Summary:"
              f"\nTotal Users Processed: {len(self.results)}")
        print("")
        print("Select from the following options:")
        print("  c - Continue")
        print("  x - Exit")
        choice = input("Enter choice: ").strip().lower()
        if choice == "x" or choice == "exit" or choice == "q" or choice == "quit" :
            logger.info("Exiting as per user request.")
            exit(0)
        

if __name__ == "__main__":
    provisioner = UserProvisioner("users.yaml")
    results = provisioner.provision_all()
    for result in results:
        print(result)