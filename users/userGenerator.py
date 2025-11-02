#!/usr/bin/env python3

# user.py
# Author: Luxforge
# User class for singlular user management tasks.


import subprocess
from pathlib import Path
import pwd
import grp
from foundry.logger import Logger 
from passwordEngine import PasswordEngine

# Initialize logger - logger env is local to this file
logger_env_path = Path(__file__) / "logger.env"
logger = Logger(logger_env_path)

class UserGenerator:
    """
    Class purely for user creation and management.
    PARAMS: config: dict - Configuration dictionary with user attributes.
    """
    GLOBAL_DEFAULTS = {
        "uid": 1000,
        "name": None,
        "uid_next_available": True,
        "gid": 1000,
        "gid_next_available": True,
        "shell": "/bin/bash",
        "home": None,
        "create_home": True,
        "default_home": True,
        "full_name": None,
        "password": None,
        "generate_password": False,
        "service": False, # If true, no login, no home dir - service account
        "ssh_key": False,
        "known_hosts": False,
        "groups": [],
        "add_groups": [],
        "remove_groups": []
    }
    VERSION = "1.0"
    def __init__(self, config: dict, defaults: dict = {}, complexity: dict = PasswordEngine.PASSWORD_COMPLEXITY, username: str = ""):

        # Set the full config
        self.config = self._resolve_config(config, defaults)
        self.defaults = defaults

        if not self.config:
            logger.error("User configuration cannot be empty.")
            raise ValueError("User configuration cannot be empty.")
        
        # All usernames need to be present
        if not self.config.get("name"):
            logger.error("User configuration must include a 'name' field.")
            raise ValueError("User configuration must include a 'name' field.")

        # Initialize username
        self.name = None
        self.user_created = False
        if not username:
            username = self.config.get("name")
        self.set_username(username=username)

        # Set basic attributes
        self.uid = None
        self.gid = None
        self.shell = None
        self.home = None
        self.password = None
        self.ssh_key = None
        self.known_hosts = None
        self.groups = []

        # Everything else is optional
        self.set_id(id_type="uid")
        self.set_id(id_type="gid")
        self.set_shell()
        self.set_home()
        self.set_full_name()
        self.set_password()
        self.set_ssh_key()
        self.add_known_hosts()
        
        # Resolve groups
        self._resolve_groups()

        # Set the user's groups
        self.add_to_groups()

    def set_username(self, username: str = "") -> None:
        """
        Sets the username for the user.
        PARAMS: username: str - The desired username.
        RETURNS: str - The validated username.
        """

        if not username:
            username = self.config.get("name")
        # Check if username is available
        try:
            entry = pwd.getpwnam(username)
            logger.warn(f"Username '{username}' already exists.")
            self.name = username
            self.user_created = True
            return
        except KeyError:
            logger.debug(f"Username '{username}' is available.")

        # Create the username
        try:
            subprocess.run(["sudo", "useradd", username], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create user '{username}': {e}")
            raise ValueError(f"Failed to create user '{username}'. {e}")
        logger.info(f"Created user '{username}'.")
        self.name = username
        self.user_created = True

    
    def is_service_account(self) -> bool:
        """
        Checks if the user is configured as a service account.
        RETURNS: bool - True if service account, False otherwise.
        """
        return self.config.get("service")
    
    def _resolve_config(self, config, defaults):
        """ Resolves the final configuration value for the user."""
        # Global defaults host all keys, start with that
        for key in self.GLOBAL_DEFAULTS:

            # If key not in config, check defaults, then global
            if key not in config:

                # If the key is in the defaults, use that
                if key in defaults:
                    logger.info(f"SECTION DEFAULT -- {key}: '{defaults[key]}'")
                    config[key] = defaults[key]
                else:
                    logger.debug(f"GLOBAL DEFAULT -- {key}: '{self.GLOBAL_DEFAULTS[key]}'")
                    config[key] = self.GLOBAL_DEFAULTS[key]
            # Key already in config, do nothing with it
            else:
                logger.info(f"USER CONFIG -- {key}: '{config[key]}'")

        return config

    def _resolve_groups(self, ):
        """ Resolves the final list of groups for the user."""
        
        logger.debug("Resolving user groups.")

        default = set(self.defaults.get("groups", []))
        logger.debug(f"default groups from default config: {default}")
        
        # Use either add or just groups
        base = set(self.config.get("groups", []))
        logger.debug(f"Base groups from config: {base}")
        add = set(self.config.get("add_groups", []))
        logger.debug(f"Groups to add from config: {add}")
        
        remove = set(self.config.get("remove_groups", []))
        logger.debug(f"Groups to remove from config: {remove}")

        self.groups = list((default | base | add) - remove)
   
    def get_next_available_id(self, id_value: int, id_type: str = "uid") -> int:
        """
        Finds the next available UID or GID starting from id_value.
        PARAMS:
            id_value: int - The starting UID or GID.
            id_type: str - Either 'uid' or 'gid'.
        RETURNS:
            int - The next available UID or GID.
        """
        while not self.id_is_available(id_value, id_type=id_type):
            id_value += 1
        return id_value

    def id_is_available(self, id_value: int, id_type: str = "uid") -> bool:
        """
        Checks if a UID or GID is available.
        PARAMS:
            id_value: int - The UID or GID to check.
            id_type: str - Either 'uid' or 'gid'.
        RETURNS:
            bool - True if available, False otherwise.
        """
        try:
            if id_type == "uid":
                pwd.getpwuid(id_value)
            elif id_type == "gid":
                grp.getgrgid(id_value)
            else:
                logger.error(f"{id_type.upper()} is not a known type.")
                raise ValueError("Invalid id_type. Must be 'uid' or 'gid'.")
            logger.warning(f"{id_type.upper()} {id_value} is already in use by {UserGenerator.get_name_by_id(id_value,id_type)}")
            return False
        except KeyError:
            logger.debug(f"{id_type.upper()} {id_value} is available.")
            return True

    def name_is_available(self, name: str = None, type: str = "user") -> bool:
        """
        Checks if a username or groupname is available.
        PARAMS:
            name: str - The username/groupname to check.
        RETURNS:
            bool - True if both username and groupname are available, False otherwise.
        """
        # First check username
        if name is None:
            name = self.name
        try:
            if type == "user":
                pwd.getpwnam(name)
            elif type == "group":
                grp.getgrnam(name)
            if self.user_created:
                logger.debug(f"{type.capitalize()} '{name}' exists and is owned by this process.")
                return False
            logger.error(f"{type.capitalize()} '{name}' is already in use.")
            raise ValueError(f"{type.capitalize()} '{name}' is already in use.")
            
        except KeyError:
            logger.debug(f"{type.capitalize()} '{name}' is available.")
        return True
    
    def set_id(self, id_type: str):
        """
        Sets UID or GID for the user, creating or modifying as needed.
        PARAMS:
            id_type: str - Either 'uid' or 'gid'.
        """
        config_key = id_type
        next_available_key = f"{id_type}_next_available"
        id_value = self.config.get(config_key)
        allow_next = self.config.get(next_available_key)

        # Check to see if the user already has the ID assigned
        if UserGenerator.identity_has_id(name=self.name, expected_id=id_value, id_type=id_type):
            logger.info(f"{id_type.upper()} {id_value} is already assigned to '{self.name}'. No changes needed.")
            setattr(self, id_type, id_value)
            return

        if not self.id_is_available(id_value, id_type) and not allow_next:
            logger.error(f"{id_type.upper()} {id_value} is already in use and '{next_available_key}' is set to False.")
            raise ValueError(f"{id_type.upper()} {id_value} is already in use and '{next_available_key}' is set to False.")

        if allow_next:
            id_value = self.get_next_available_id(id_value, id_type)

        # Determine entity type and command mapping
        entity_type = "group" if id_type == "gid" else "user"
        id_flag = "-g" if id_type == "gid" else "-u"
        create_cmd = ["sudo", f"{entity_type}add"]
        modify_cmd = ["sudo", f"{entity_type}mod"]

        # Check if entity exists
        exists = not self.name_is_available(name=self.name, type=entity_type)

        if exists:
            subprocess.run(modify_cmd + [id_flag, str(id_value), self.name], check=True)
            logger.info(f"Modified {entity_type} '{self.name}' to have {id_type.upper()} {id_value}.")
        else:
            subprocess.run(create_cmd + [id_flag, str(id_value), self.name], check=True)
            logger.info(f"Created {entity_type} '{self.name}' with {id_type.upper()} {id_value}.")

        # Set the attribute
        setattr(self, id_type, id_value)

    def set_shell(self):
        """ Sets the user's shell."""

        # Nothing to check here really, just update the user's shell
        shell = self.config.get("shell")

        # Override shell to nologin for service accounts
        if self.is_service_account() and shell != "/usr/sbin/nologin":
            logger.warning(f"Overriding shell to /usr/sbin/nologin for service account '{self.name}'.")
            shell = "/usr/sbin/nologin"
        subprocess.run(["sudo", "usermod", "-s", shell, self.name], check=True)
        self.shell = shell

    def validate_password(self, password: str) -> bool:
        """ Validates the password against complexity requirements."""
        # Password complexity checks can be added here
        # Set local complexities here but can be modified later
        self.password_engine.set_complexity(self.config.get("password_complexity", PasswordEngine.PASSWORD_COMPLEXITY))
        return self.password_engine.validate_password(password)
    
    def set_password(self, password: str = None, generate: bool = None):
        """ Sets the user's password, generating one if specified."""
        if self.is_service_account():
            logger.debug(f"User '{self.name}' is a service account; skipping password setup.")
            return
        if generate is None:
            generate = self.config.get("generate_password")
            logger.info(f"Using configured generate_password for '{self.name}': {generate}.")
        
        if password is None:
            password =  self.config.get("password")
            if password is not None:
                logger.info(f"Using configured password for '{self.name}' - password: {password}.")        
        if generate:
            password = PasswordEngine.generate_password()
            logger.info(f"Generated password for '{self.name}'. Password: {password}")
        elif not password:
            logger.error("Password must be provided or generate=True must be set.")
            raise ValueError("Password must be provided or generate=True must be set.")

        subprocess.run(["sudo", "chpasswd"], input=f"{self.name}:{password}".encode(), check=True)
        logger.info(f"Password set for user '{self.name}'.")
        self.password = password

    def group_exists(self, group: str) -> bool:
        try:
            grp.getgrnam(group)
            return True
        except KeyError:
            return False

    def gid_unavailable_prompt(self, gid: int) -> bool:
        """ Prompts the user if a GID is unavailable."""
        print(f"GID {gid} is already in use.")
        print("Select from the below options:")
        print("  [n] Specify a different GID")
        print("  [a] Auto-assign next available GID")
        print("  [e] Exit the process -- default option")
        print("")
        while True:
            action = input("Enter 'n' to specify, 'a' to auto-assign, or 'e' to exit -- default [n/a/X]: ").strip().lower()

            # Handle user input - loops until resolved or recalls this method
            if action == 'n':
                input_gid = input("Enter a different GID: ").strip()
                return self.create_group_with_gid(self, gid=input_gid)

            # Auto-assign next available GID
            elif action == 'a':
                next_gid = self.get_next_available_id(gid, id_type="gid")
                logger.info(f"Auto-assigning next available GID {next_gid}.")
                return self.create_group_with_gid(self, gid=next_gid)
            
            # exit option
            elif action == 'e' or action == '' or action == 'x':
                logger.error(f"Exiting due to unavailable GID {gid}.")
                raise SystemExit(f"GID {gid} is unavailable. Exiting.")
            
            # invalid input
            else:
                logger.warning("Invalid input. Please enter 'n', 'a', or 'e'.")

    def create_group_with_gid(self, group: str, gid: int) -> bool:
        """ Creates a group with a specified GID."""
        
        # Check if GID is viable
        try:
            gid = int(gid)     
        except ValueError:
            logger.error("Invalid GID input. Please enter a numeric value.")
            return self.create_group(group)

        # Check if GID is available    
        if not self.id_is_available(gid, id_type="gid"):

            # GID is unavailable, prompt user for action - enters a loop until resolved or recalls this method
            self.gid_unavailable_prompt(self, gid)
        
        # Create the group with the specified GID
        try:
            subprocess.run(["sudo", "groupadd", "-g", str(gid), group], check=True)
            logger.info(f"Group '{group}' created with GID {gid}.")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create group '{group}' with GID {gid}: {e}")
            raise ValueError(f"Failed to create group '{group}' with GID {gid}. {e}")

    def create_group(self, group: str) -> bool:
        """ Asks the user if they want to create a missing group."""
        # Warn the group does not exist, ask user to create, skip or exit
        logger.warning(f"Group '{group}' does not exist. What would you like to do?")
        print(f"Group '{group}' does not exist.")
        print("\nSelect from the below options:")
        print("  [c] Create the group")
        print("  [s] Skip adding to this group")
        print("  [e] Exit the process -- default option")
        print("")
        while True:
            action = input("Enter 'c' to create, 's' to skip, or 'x' to exit -- default [c/s/X]: ").strip().lower()
            if action == 'c':
                gid = None
                # Check if user wants to specify a GID
                gid_input = input(f"Enter GID for group '{group}' or press Enter to auto-assign (takes the next available ID after this user's ID): ").strip()
                if gid_input:
                    return self.create_group_with_gid(group, gid_input) 
                subprocess.run(["sudo", "groupadd", "-g", str(gid), group], check=True)
                logger.info(f"Group '{group}' created.")
                return True
                
            elif action == 's':
                logger.info(f"Skipping creation of group '{group}'.")
                return False
                
            elif action == 'e' or action == '' or action == 'x':
                logger.error(f"Exiting due to missing group '{group}'.")
                raise SystemExit(f"Missing group '{group}'. Exiting.")

            else:
                logger.warning("Invalid input. Please enter 'c', 's', or 'e'.")

    def add_to_groups(self):
        """ Adds the user to the resolved groups."""

        actual_groups_added = []
        for group in self.groups:
            logger.debug(f"Checking group '{group}' for user '{self.name}'.")

            # Check if group exists
            if not self.group_exists(group):
                
                # get user decision on creating group
                if not self.create_group(group):
                    logger.info(f"Skipping adding user '{self.name}' to group '{group}'.")
                    continue
            
            # Add user to group
            logger.d(f"Adding user '{self.name}' to group '{group}'.")
            try:
                subprocess.run(["sudo", "usermod", "-aG", group, self.name], check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to add user {self.name} to group {group}: {e}")
                raise ValueError(f"Failed to add user {self.name} to group {group}. {e}")
            
            # Success log
            logger.info(f"User '{self.name}' added to group '{group}'.")
            actual_groups_added.append(group)
        self.groups = actual_groups_added

    def set_ssh_key(self):
        """Generates an SSH key pair for the user."""
        if self.is_service_account():
            logger.debug(f"User '{self.name}' is a service account; skipping SSH key generation.")
            return

        if not self.home:
            logger.error("Home directory must be set before generating SSH keys.")
            raise ValueError("Home directory must be set before generating SSH keys.")

        if not self.config.get("ssh_key"):
            return

        logger.debug(f"Generating SSH key for user '{self.name}'.")
        ssh_dir = Path(self.home) / ".ssh"
        
        # Check if ssh dir exists, create if not
        if not ssh_dir.exists():
            logger.info(f"Creating .ssh directory for user '{self.name}'.")
            # Sudo create .ssh directory
            subprocess.run(["sudo", "mkdir", "-p", str(ssh_dir)], check=True)
        else:
            logger.warning(f".ssh directory already exists for user '{self.name}'. Skipping creation.")
            return
        
        # Enforce ownership and permissions using sudo
        logger.info(f"Generating SSH key for user '{self.name}' with sudo elevation.")
        subprocess.run(["sudo", "chown", f"{self.name}:{self.name}", str(ssh_dir)], check=True)
        subprocess.run(["sudo", "chmod", "700", str(ssh_dir)], check=True)

        key_path = ssh_dir / "id_rsa"
        subprocess.run([
            "sudo", "ssh-keygen", "-t", "rsa", "-b", "4096",
            "-f", str(key_path), "-N", ""
        ], check=True)

        subprocess.run(["sudo", "chown", f"{self.name}:{self.name}", str(key_path)], check=True)
        subprocess.run(["sudo", "chown", f"{self.name}:{self.name}", str(key_path.with_suffix(".pub"))], check=True)

        self.ssh_key = True
        logger.info(f"Generated SSH key for user '{self.name}' with sudo elevation.")

    
    @staticmethod
    def user_exists(username: str) -> bool:
        try:
            pwd.getpwnam(username)
            return True
        except KeyError:
            return False

    @staticmethod
    def get_name_by_id(id_value: int, id_type: str = "uid") -> str | None:
        """
        Returns the username or group name associated with a UID or GID.
        - id_type: "uid" or "gid"
        """
        if id_type == "uid":
            with open("/etc/passwd", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) >= 3 and parts[2].isdigit() and int(parts[2]) == id_value:
                        return parts[0]
        elif id_type == "gid":
            with open("/etc/group", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) >= 3 and parts[2].isdigit() and int(parts[2]) == id_value:
                        return parts[0]
        return None
    
    @staticmethod   
    def identity_has_id(name: str, expected_id: int, id_type: str = "uid") -> bool:
        """
        Checks if a user or group has the expected UID or GID.
        - id_type: "uid" or "gid"
        """
        if id_type == "uid":
            with open("/etc/passwd", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) >= 3 and parts[0] == name and parts[2].isdigit():
                        return int(parts[2]) == expected_id
        elif id_type == "gid":
            with open("/etc/group", "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) >= 3 and parts[0] == name and parts[2].isdigit():
                        return int(parts[2]) == expected_id
        return False

    def add_known_hosts(self, source="./known_hosts"):
        """ Adds known_hosts file for the user from a source file.
        PARAMS:
            source: str - Path to the source known_hosts file.
        """
        
        if self.is_service_account():
            logger.debug(f"User '{self.name}' is a service account; skipping known_hosts setup.")
            return

        if not self.config.get("known_hosts"):
            return

        src = Path(source)

        if src.exists():
            dst = Path(self.home) / ".ssh" / "known_hosts"
            dst.write_text(src.read_text())
            self.known_hosts = True
            logger.info(f"Added known_hosts for user {self.name} from {source}.")
    
    def emit_user_tag(self) -> dict:
        return {
            "username": self.name,
            "uid": self.uid,
            "gid": self.gid,
            "shell": self.shell,
            "home": self.home,
            "groups": self.groups,
            "service": self.is_service_account(),
            "ssh_key": self.ssh_key,
            "known_hosts": self.known_hosts,
            "password_entropy": PasswordEngine.estimate_entropy(self.password) if self.password else None,
            "source": "LuxForge Foundry UserGenerator v" + self.VERSION
        }
    def emit_artifact(self) -> dict:
        """
        Emits a structured artifact representing the provisioned user.
        RETURNS: dict - User artifact with all relevant attributes.
        """
        artifact = self.emit_user_tag()
        return artifact
    

    @staticmethod
    def delete_user(username: str):
        """
        Deletes a Linux user and their home directory.
        Requires root privileges.
        """
        # Check username
        if not username:
            logger.error("Username must be provided to delete a user.")
            raise ValueError("Username must be provided to delete a user.")
        
        # Check if user exists
        if not UserGenerator.user_exists(username):
            print(f"❌ User '{username}' does not exist. Cannot delete.")
            return

         # Proceed to delete the user
        try:
            subprocess.run(["sudo", "userdel", "--remove", username], check=True)
            subprocess.run(["sudo", "rm", "-rf", f"/home/{username}"], check=True)
            logger.info(f"Deleted user '{username}' with home directory.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete user '{username}': {e}")


    def provision_user(self):
        tag = self.emit_user_tag()
        logger.info(f"Provisioned user '{self.name}' with UID {self.uid}, GID {self.gid}.")
        return tag
    
    def set_home(self):
        """
        Sets the user's home directory and ensures it exists with correct ownership.
        """
        # Skip if this is to be a service account
        if self.is_service_account():
            logger.debug(f"User '{self.name}' is a service account; skipping home directory setup.")
            return
        
        home = self.config.get("home")
        if not home:
            if self.config.get("create_home"):
                home = f"/home/{self.name}"
            else:
                # Just skip if no home is to be created
                logger.debug(f"No home directory set for user '{self.name}'. Skipping home setup.")
                return
            
        # Update the user's home directory reference
        subprocess.run(["sudo", "usermod", "-d", home, self.name], check=True)

        # Create the directory if it doesn't exist
        subprocess.run(["sudo", "mkdir", "-p", home], check=True)

        # Set ownership to the user
        subprocess.run(["sudo", "chown", f"{self.name}:{self.name}", home], check=True)

        # Optionally set permissions
        subprocess.run(["sudo", "chmod", "755", home], check=True)

        self.home = home
        logger.info(f"Set home directory for '{self.name}' to '{home}' and ensured it exists.")

    def set_full_name(self):
        """
        Sets the user's full name (GECOS field).
        """
        full_name = self.config.get("full_name")
        if not full_name:
            logger.debug(f"No full name provided for user '{self.name}'. Skipping full name setup.")
            return
        subprocess.run(["sudo", "usermod", "-c", full_name, self.name], check=True)
        logger.info(f"Set full name for user '{self.name}' to '{full_name}'.")
        self.full_name = full_name

def run_smoke_tests(test_configs: list):
    """
    Runs smoke tests on a list of user configs.
    Logs pass/fail for each provisioning pivot.
    """
    results = []

    for config in test_configs:
        name = config.get("name", "unnamed")
        logger.info(f"🧪 Starting smoke test for '{name}'")

        try:
            ug = UserGenerator(config=config)
            artifact = ug.emit_artifact()

            results.append({
                "name": name,
                "status": "PASS",
                "uid": artifact.get("uid"),
                "gid": artifact.get("gid"),
                "groups": artifact.get("groups"),
                "shell": artifact.get("shell"),
                "home": artifact.get("home"),
                "service": artifact.get("service"),
                "entropy": artifact.get("password_entropy"),
            })

            logger.info(f"✅ Smoke test passed for '{name}'")

        except Exception as e:
            logger.error(f"❌ Smoke test failed for '{name}': {e}")
            results.append({
                "name": name,
                "status": "FAIL",
                "error": str(e)
            })

    return results

def load_test_configs(file_path: str = "test_configs.yaml") -> list:
    """
    Loads a list of test user configs from a YAML file.
    """
    import yaml
    from pathlib import Path
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Test config file not found: {file_path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        raise ValueError("YAML file must contain a list of user config dictionaries.")

    logger.info(f"Loaded {len(data)} test configs from '{file_path}'")
    return data

if __name__ == "__main__":
    test_configs = load_test_configs()
    run_smoke_tests(test_configs)
