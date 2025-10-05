#!/usr/bin/env python3

# LuxForge Launcher
# Author: Luxforge

import os
import sys
from pathlib import Path

# Load Logger
from luxforge.logger import Logger
# Load menu functions
from luxforge.menu import show_menu

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent
TRIAL_SCRIPT = PROJECT_ROOT / "tests" / "trial_envprofile.py"
SETUP_SCRIPT = PROJECT_ROOT / "setup" / "setup_envprofile.sh"

# Load logger
def run_trial():
    print("[+] Running trial_envprofile.py")
    os.system(f"{sys.executable} {TRIAL_SCRIPT}")

def run_setup():
    print("[+] Running setup_envprofile.sh")
    os.system(f"bash {SETUP_SCRIPT}")

def main():
    while True:
        show_menu()
        choice = input("[?] Select an option: ").strip()
        if choice == "1":
            run_trial()
        elif choice == "2":
            run_setup()
        elif choice == "3":
            print("[+] Exiting LuxForge Launcher")
            break
        else:
            print("[!] Invalid choice. Try again.")

if __name__ == "__main__":
    main()