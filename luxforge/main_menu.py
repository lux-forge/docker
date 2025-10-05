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
    }
    menu_name = "Main Menu"
    
    def load_docker_menu(self):
        from docker.menu import DockerMenu
        DockerMenu(previous_menu=self).launch()
        

if __name__ == "__main__":
    menu = MainMenu()
    menu.launch()