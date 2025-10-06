# /#!/usr/bin/env python3

# users.py
# Author: Luxforge
# User management for Luxforge tools and docker containers

from utils.pathloader import paths
import re
from menu import Menu
# Load the other classes and functions
from utils.logger import logger

class UserMenu(Menu):
    """
    Interactive CLI menu for user management tasks.
    """
    options_new = {
        # Desc - Display Name - Method Name - Callable Values. Will need to upgrade all submenus to this format
        "A": ("Add User", "add_user",("A","add","adduser","addusers","new","newuser","newusers")),
        "D": ("Delete User", "delete_user",("D","delete","deleteuser","deleteusers")),
        "L": ("List Users", "list_users",("L","list","listusers")),
        "C": ("Create Users from File", "create_users_from_file",("C","create","createusers","createusersfromfile","createusersfromcsv","createusersfromtxt")),
    }

    options = {
        "C": ("Create User", "create_user"),
        "D": ("Delete User", "delete_user"),
        "L": ("List Users", "list_users"),
        "F": ("Create Users from File", "create_users_from_file"),
    }
    menu_name = "User Management Menu"

    
    def create_user(self, 
                    username: str = None, 
                    password: str = None, 
                    uid: int = None, 
                    gid: int = None, 
                    home_dir: bool = None, 
                    shell: str = "/bin/bash", 
                    service_account: bool = False,
                    ssh_key: bool = False,
                    known_hosts: bool = False
                    ):
        """
        Create a new user with the given parameters.
        PARAMS: username: str - The username for the new user.
                password: str - The password for the new user.
                uid: int - The user ID for the new user.
                gid: int - The group ID for the new user.
                home_dir: str - The home directory for the new user.
                shell: str - The login shell for the new user.
                service_account: bool - Whether this is a service account (no login).
                ssh_key: bool - Whether to generate SSH keys for the user.
                known_hosts: bool - Whether to set up known_hosts for the user.
        RETURNS: None
        """
        # No validation required
        
        # Load the environment variables
        self.__load_env_variables()
        
        # Create the username
        username = self.__create_username(username=username)    

        # Pivot to creating a service account if specified
        if service_account:
            self.__create_service_account(username=username)
            return

        if not password:
            password = input("Enter the password: ")
        if not uid:
            uid = input("Enter the UID (or press Enter to skip): ")
            uid = int(uid) if uid else None
        if not gid:
            gid = input("Enter the GID (or press Enter to skip): ")
            gid = int(gid) if gid else None
        if not home_dir:
            home_dir = input("Enter the home directory (or press Enter to skip): ")
        if not shell:
            shell = input("Enter the login shell (or press Enter to skip): ")
        if not ssh_key:
            ssh_key = input("Generate SSH key? (y/n): ").lower() == "y"
        if not known_hosts:
            known_hosts = input("Set up known_hosts? (y/n): ").lower() == "y"

        print(f"User {username} created successfully.")

    def __load_env_variables(self):
        # Pull all the env files within the users dir
        import os
        from utils.envprofile import EnvProfile
        from utils.files import find_all_files

        
        env = EnvProfile()

        env_files = find_all_files(f"{paths.luxforge}/users/", "*.env")

        # Extract the example env file
        for file in env_files:
            if file.name == "EXAMPLE.env":
                example_env_file = file
                env_files.remove(file)
                break
        
        # Check if there are any other env files
        if not env_files:
            env_files = [example_env_file] 
            print(f"[WARNING] No user .env files found in {paths.luxforge}/users/. Using example file: {example_env_file}")
            # Save the env file to the users dir
            os.makedirs(f"{paths.luxforge}/users/", exist_ok=True)
            import shutil
            shutil.copy(example_env_file, f"{paths.luxforge}/users/changeme.env")
            print(f"[INFO] Created example user .env file: {paths.luxforge}/users/changeme.env")
        
        # Load the env files
        env.load_keys(env_files, skip_list=[])

        # Now we can use the env variables - they're available in env_profile.loaded_keys and os.environ

    def validate_username(self, username: str=None) -> list:
        """
        Validate a username based on common Linux username rules.
        PARAMS: username: str - The username to validate.
        RETURNS: list - A list of validation error messages. Empty if valid.
        """
        import re # For regex matching
        import pwd # For checking existing users
        
        logger.debug(f"Validating username: {username}")
        # Check it's a string
        if not isinstance(username, str):
            logger.error(f"Invalid username provided: {username}. Must be a string.")
            return False
        logger.debug(f"Username is a string: {username}")
        
        # Not empty
        if not username:
            logger.error("Username is empty")
            return False
        logger.debug(f"Username is not empty: {username}")

        # Must start with a letter or underscore
        if not re.match(r'^[a-zA-Z_]', username):
            logger.error("Username starts with invalid character (must start with a letter or underscore)")
            return False
        logger.debug(f"Username starts with a valid character: {username}")

        # Only valid characters (letters, digits, underscores, hyphens)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', username):
            logger.error("Contains invalid characters (only letters, digits, underscores, hyphens allowed)")
            return False
        logger.debug(f"Username contains all valid characters: {username}")

        # Length ≤ 32
        if len(username) > 32:
            logger.error("Username too long (max 32 characters)")
            return False
        logger.debug(f"Username length is valid: {len(username)} characters")

        # Already exists
        try:
            pwd.getpwnam(username)
            logger.error(f"Username '{username}' already exists")
            return False
        
        except KeyError:
            pass  # Username is available

        logger.debug(f"Username '{username}' is available")
        return True

    def __create_username(self, username: str = None) -> str:
        # Create a username if not provided. Forces loop ubtil valid
        if not username:
            username = input("Enter a username: ")
            while not self.validate_username(username):
                username = input("Enter a valid username: ")
        return username

    def __create_service_account(self, username: str = None):
        """
        Create a new service account with no login shell.
        PARAMS: username: str - The username for the new service account.
        RETURNS: None
        """
        self.create_user(username=username, service_account=True)
       
    def delete_user(self):
        username = input("Enter the username to delete: ")
        # Logic to delete user goes here
        print(f"User {username} deleted successfully.")
        
    def list_users(self):
        # Logic to list users goes here
        users = ["user1", "user2", "user3"]  # Example user list
        print("Current users:")
        for user in users:
            print(f"- {user}")
