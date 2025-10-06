# /usr/bin/env python3

# menu.py
# Author: Luxforge
# Synth Data Menu

from menu import Menu
from luxforge.utils.logger import logger
from synth_data import SynthData
from luxforge.utils.pathloader import paths

class SynthDataMenu(Menu):
    """
    Interactive CLI menu for managing synthetic data generation tasks.
    """
    options = {
        "G": ("Generate Synthetic Data", "generate_synthetic_data"),
        "V": ("View Generated Data", "view_generated_data"),
        "C": ("Configure Data Parameters", "configure_data_parameters"),
    }
    menu_name = "Synthetic Data Menu"
    
    def generate_synthetic_data(self):
        synth_data = SynthData()
        synth_data.generate_data()
        input("Press Enter to return to the menu...")
    
    def view_generated_data(self):
        synth_data = SynthData()
        synth_data.view_data()
        input("Press Enter to return to the menu...")

    def configure_data_parameters(self):
        synth_data = SynthData()
        synth_data.configure_parameters()
        input("Press Enter to return to the menu...")