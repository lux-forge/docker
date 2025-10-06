#!/usr/bin/env python3

# main_menu.py
# Author: Luxforge
# Main menu launcher for Luxforge tools


from menu import Menu
# Load the other classes and functions

class MainMenu(Menu):
    """
    Interactive CLI menu for management tasks.
    """
    options = {
        "D": ("Docker", "load_docker_menu"),
        "P": ("Load Paths", "load_paths_menu"),
        "U": ("User Management", "load_user_menu"),
        "G": ("Games", "load_games_menu"),
    }
    menu_name = "Main Menu"
    
    def load_docker_menu(self):
        from docker.menu import DockerMenu
        DockerMenu(previous_menu=self).launch()
    
    def load_paths_menu(self):
        from utils.pathloader import paths
        paths.print_paths()
        input("Press Enter to return to the menu...")
    
    def load_user_menu(self):
        from users.users import UserMenu
        UserMenu(previous_menu=self).launch()
    
    def load_games_menu(self):
        from games.menu import GamesMenu
        GamesMenu(previous_menu=self).launch()

if __name__ == "__main__":
    menu = MainMenu()
    menu.launch()