# /#!/usr/bin/env python3

# menu.py
# Author: Luxforge
# Menu to host the games

from menu import Menu
from utils.logger import logger

class GamesMenu(Menu):
    """
    Interactive CLI menu for games.
    """
    options = {
        "C": ("Chess", "play_chess"),
        "T": ("Tic-Tac-Toe", "play_tic_tac_toe"),
        "L": ("Lottery", "load_lottery_menu")
    }
    menu_name = "Games Menu"
    
    def play_chess(self):
        logger.info("Project for another time perhaps.")
        input("Press Enter to return to the menu...")
    
    def play_tic_tac_toe(self):
        logger.info("Project for another time perhaps.")
        input("Press Enter to return to the menu...")

    def load_lottery_menu(self):
        from games.lottery import LotteryMenu
        LotteryMenu(previous_menu=self).launch()