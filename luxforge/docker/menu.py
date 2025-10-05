#!/usr/bin/env python3

# docker_menu.py
# Author: Luxforge
# Docker menu launcher for docker tools


from menu import Menu
# Load the other classes and functions

class DockerMenu(Menu):
    """
    Interactive CLI menu for Docker management tasks.
    """
    options = {
        "N": ("Networking", "load_docker_menu"),
        "V": ("Check Volumes", "load_volume_menu"),
    }
    menu_name = "Docker Menu"
    
    def load_docker_menu(self):
        from docker.networking import DockerNetworkMenu
        DockerNetworkMenu(previous_menu=self).launch()

if __name__ == "__main__":
    docker_menu = DockerMenu()
    docker_menu.launch()