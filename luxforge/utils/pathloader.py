# pathloader.py
# Author: Luxforge
# Centralized path resolver for repo-rooted assets

import os
from pathlib import Path

class PathLoader:
    def __init__(self):
        import os
        self.root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

        # Search the repo root for dirs and create properties
        for dir_name in os.listdir(self.root):
            dir_path = self.root / dir_name
            if os.path.isdir(dir_path):

                # Return the path as a Path object
                setattr(self, dir_name, Path(dir_path))
        
    # Test the paths
    def print_paths(self):
        paths = self.__dict__
        print("Resolved Paths:")

        # Retrieve the properties dynamically
        for key, value in paths.items():
            if not key.startswith("_") and not callable(getattr(self, key)):
                print(f"  {key}: {value}")

paths = PathLoader()
if __name__ == "__main__":
    paths.print_paths()