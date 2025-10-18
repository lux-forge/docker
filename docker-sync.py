#!/usr/bin/env python3

# docker-sync.py
# Script to update a node's configuration from the NAS server.

import os
import shutil
from pathlib import Path
from filecmp import cmp
from typing import Literal

class DockerSync:
    """
    Class to handle synchronization of Docker configuration files
    between a master directory (e.g., on a NAS) and a host directory
    (e.g., on a Docker node).
    """

    IGNORE_DIRS = {".git", "__pycache__", ".vscode", ".idea", ".luxforge-venv", "logs","backup"}
    def __init__(self, master_path="/mnt/docker", host_path="/docker"):
        self.master = Path(master_path)
        self.host = Path(host_path)

    def validate(self):
        if not self.master.is_dir():
            raise FileNotFoundError(f"Master path not found: {self.master}")
        if not self.host.is_dir():
            raise FileNotFoundError(f"Host path not found: {self.host}")

        print(f"[✓] Validated paths:\n    Master: {self.master}\n    Host: {self.host}")

    def sync(self, direction: Literal["push", "pull"], mirror=None):
        src = self.host if direction == "push" else self.master
        dst = self.master if direction == "push" else self.host

        print(f"[↔] Syncing {direction.upper()}: {src} → {dst}")
        self._sync_dir(src, dst)
        
        # Remove deleted files in mirror mode
        if mirror is None:
            # If mirror is not specified, ask the user
            mirror_input = input("Enable mirror mode (remove files in destination not present in source)? [y/N]: ").lower()
            mirror = mirror_input == 'y'
        
        if mirror:
            print("[!] Mirror mode enabled: Removing deleted files in destination.")

            # Confirm with user
            confirm = input("Are you sure you want to proceed? This will delete files in the destination that do not exist in the source. [y/N]: ").lower()
            if confirm == 'y':
                self._remove_deleted(src, dst)
        print("[✓] Sync complete.")    

    def _sync_dir(self, src_dir: Path, dst_dir: Path):
        """ 
        Recursively sync files from src_dir to dst_dir 
        PARAMS:
            src_dir: Source directory (Path)
            dst_dir: Destination directory (Path)
        """
        for root, _, files in os.walk(src_dir):
            rel = os.path.relpath(root, src_dir)
            
            # Skip ignored directories
            if any(part in self.IGNORE_DIRS for part in Path(rel).parts):
                continue
            
            # Create target directory path
            target_root = dst_dir / rel
            target_root.mkdir(parents=True, exist_ok=True)

            # Sync files
            for file in files:
                src_file = Path(root) / file
                dst_file = target_root / file
                self._sync_file(src_file, dst_file)

    def _sync_file(self, src: Path, dst: Path):
        """ Sync a single file from src to dst """
        
        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Skip if destination is newer or unchanged
        if dst.exists():

            # Check if destination is newer
            if dst.stat().st_mtime > src.stat().st_mtime:
                print(f"[!] Destination newer: {dst}")
                input("We have a newer file, might want to check it, skipping for now...")  # Pause for user confirmation

            if cmp(src, dst, shallow=False):
                print(f"[-] Skipping unchanged: {dst}")
                return

        shutil.copy2(src, dst)
        print(f"[✓] Synced: {src} → {dst}")

    def _remove_deleted(self, src_dir: Path, dst_dir: Path):
        """ Remove files in dst_dir that no longer exist in src_dir """
        for root, _, files in os.walk(dst_dir):
            rel = os.path.relpath(root, dst_dir)

            # Skip ignored directories
            if any(part in self.IGNORE_DIRS for part in Path(rel).parts):
                continue

            
            src_root = src_dir / rel

            for file in files:
                dst_file = Path(root) / file
                src_file = src_root / file

                if not src_file.exists():
                    dst_file.unlink()
                    print(f"[×] Removed: {dst_file}")

    def menu(self):
        options = ["Push", "Pull", "Exit"]

        while True:
            os.system('clear')
            print("Select sync direction:\n")
            for i, option in enumerate(options):
                if i == len(options) - 1:
                    print("\nX. Exit")
                else:
                    print(f"{i+1}. {option}")

            key = input("\nEnter to select: ").lower()

            if key == "1":
                print(f"\n[.menu.select.audit] Selected: PUSH")
                confirm = input("This will PUSH local changes to master. Continue? [y/N]: ").lower()
                if confirm == "y":
                    self.sync("push")
                else:
                    print("Push aborted.")

            elif key == "2":
                print(f"\n[.menu.select.audit] Selected: PULL")
                confirm = input("This will OVERWRITE local files from master. Continue? [y/N]: ").lower()
                if confirm == "y":
                    self.sync("pull")
                else:
                    print("Pull aborted.")

            elif key == "x" or key == "exit":
                print("Exiting.")
                break

            else:
                print(f"\n[!] Invalid selection: {key}")



if __name__ == "__main__":
    syncer = DockerSync()
    try:
        syncer.validate()
        syncer.menu()
    except Exception as e:
        print(f"[!] Error: {e}")