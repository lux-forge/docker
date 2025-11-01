#!/docker/.luxforge-venv/bin/python3
# userMenu.py
# Author: Luxforge
# Interactive CLI menu for user management tasks.

from pathlib import Path
from foundry.menu import Menu
# Load the other classes and functions
from foundry.logger import Logger

import subprocess, pwd, grp
from tabulate import tabulate
from rich.console import Console
from rich.table import Table


# Initialize logger - logger env is local to this file
logger_env_path = Path(__file__) / "logger.env"
print(f"Loading logger env from: {logger_env_path}")
logger = Logger(logger_env_path)


class UserMenu(Menu):
    """
    Interactive CLI menu for user management tasks.
    """
    MENU_META = {
        "name": "UserMenu",  # Display name
        "desc": "Menu for managing users"  # Description
    }
    def _set_options(self):
        self.options = {
            "C": ("Create User", self.create_user),
            "D": ("Delete User", self.delete_user),
            "L": ("List Users", self.list_users),
            "F": ("Create Users from File", self.create_users_from_file),
        }    
    def create_user(self):
        """
        Create a new user interactively.
        PARAMS: None
        RETURNS: None
        """
        username = input("Enter a username (leave blank to prompt): ")
        username = self.__create_username(username=username)

        is_service_account = input("Is this a service account? (y/n): ").strip().lower() == "y"
        from userGenerator import UserGenerator
        UserGenerator(username=input("Enter username: "))
        

    def validate_username(self, username: str="") -> list | bool:
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
            logger.warn(f"Username '{username}' already exists")
            return True
        
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
        
        from userGenerator import UserGenerator
        UserGenerator.delete_user(username=username)
        input("Press Enter to return to the menu...")

    def __get_all_user_details(self) -> list:
        """
        Returns a list of dicts with full metadata for all users.
        Each dict includes: username, uid, gid, shell, home, primary_group, groups.
        """
        users = []

        # Iterate over all users in the system
        for entry in pwd.getpwall():
            users.append({
                "username": entry.pw_name,
                "uid": entry.pw_uid,
                "gid": entry.pw_gid,
                "shell": entry.pw_shell,
                "home": entry.pw_dir,
                "primary_group": grp.getgrgid(entry.pw_gid).gr_name,
                "groups": [g.gr_name for g in grp.getgrall() if entry.pw_name in g.gr_mem]
            })
        return users


    def list_users(self) -> None:
        """
            List all users on the system.
            RETURNS: None
            """
        console = Console()
        all_users = sorted(self.__get_all_user_details(), key=lambda u: u["uid"])

        real_users = [u for u in all_users if u["uid"] >= 1000 and u["shell"] not in ["/usr/sbin/nologin", "/bin/false"]]
        service_users = [u for u in all_users if u["uid"] < 1000 or u["shell"] in ["/usr/sbin/nologin", "/bin/false"]]

        def render_table(title, users, style):
            table = Table(title=title, style=style, header_style="bold")
            table.add_column("Username")
            table.add_column("UID", justify="right")
            table.add_column("GID", justify="right")
            table.add_column("Home")
            table.add_column("Shell")

            for u in users:
                is_sudo = "sudo" in u["groups"]
                style = "bold red" if is_sudo else None
                table.add_row(u["username"], str(u["uid"]), str(u["gid"]), u["home"], u["shell"], style=style)

            console.print(table)

        render_table("🧑 Real Users", real_users, "green")
        render_table("🔧 Service Accounts", service_users, "cyan")
        input("Press Enter to continue...")

    def create_users_from_file(self):
        # Uses the userprovisioner class to create users from a file
        from userProvisioner import UserProvisioner
       
        provisioner = UserProvisioner()
        results = provisioner.provision_all()
        for result in results:
            print(result)
        input("Press Enter to return to the menu...")


if __name__ == "__main__":
    menu = UserMenu()
    menu.launch()