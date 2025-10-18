#!/usr/bin/env python3

import os
from foundry.logger import Logger
from foundry.menu import Menu
from datetime import datetime
import pandas as pd

# Get the full path of this file to set as env_path
env_path = os.path.join(os.path.abspath(__file__),".env")
logger = Logger(env_path=env_path)
logger.d("Initializing vol-sync script")
logger.task="vol-sync"

class FileSyncMenu(Menu):
    """Menu for FileSync operations."""

    MENU_META = {
        "name": "File Sync Menu",
        "description": "Menu for Syncing volumes for docker containers in a swarm. Manually",
    }



    def __init__(self):
        super().__init__()
        
        # Initialize master list
        self.master_list = {}

    def _set_options(self):
        self.options = {
            # TBC
        }



class SyncTable:
    """Class to build a synchronization table for files across volumes."""

    VOLUMES = {
        "joyeuse": "/vols/joyeuse",
        "kemel": "/vols/kemel",
        "charlemagne": "/vols/charlemagne",
        "voluspa": "/vols/voluspa"
    }
    
    def build(self):
        rows = []

        # Step 1: Traverse each volume
        for node, root in self.volumes.items():
            for dirpath, _, filenames in os.walk(root):
                for fname in filenames:
                    full_path = os.path.join(dirpath, fname)
                    rel_path = os.path.relpath(full_path, root)
                    try:
                        ts = datetime.fromtimestamp(os.path.getmtime(full_path))
                        rows.append({
                            "rel_path": rel_path,
                            "node": node,
                            "full_path": full_path,
                            "timestamp": ts
                        })
                    except Exception as e:
                        print(f"[{node}] Error reading {full_path}: {e}")

        # Step 2: Create raw DataFrame
        df_raw = pd.DataFrame(rows)

        # Step 3: Pivot to wide format
        df_pivot = df_raw.pivot_table(index="rel_path", columns="node", values="timestamp", aggfunc="max")

        # Step 4: Resolve latest version
        df_latest = df_pivot.max(axis=1).rename("latest_ts")
        df_source = df_pivot.idxmax(axis=1).rename("latest_node")

        # Step 5: Flag needs
        df_flags = df_pivot.lt(df_latest, axis=0) | df_pivot.isna()
        df_flags = df_flags.fillna(True)  # missing file = needs update

        # Step 6: Merge metadata
        df = pd.concat([df_flags, df_latest, df_source], axis=1).reset_index()

        return df

    def get_targets(self, node):
        """Return list of rel_paths that node needs"""
        return self.df[self.df[node] == True]["rel_path"].tolist()

    def get_full_sync_map(self, node):
        """Return list of (rel_path, source_node, source_path) for files node needs"""
        subset = self.df[self.df[node] == True]
        return [
            (
                row["rel_path"],
                row["latest_node"],
                os.path.join(self.volumes[row["latest_node"]], row["rel_path"])
            )
            for _, row in subset.iterrows()
        ]


if __name__ == "__main__":
    menu = FileSyncMenu()
    menu.launch()
    logger.d("Exiting vol-sync script")