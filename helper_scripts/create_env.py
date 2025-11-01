#! /usr/bin/env python3

# Script to create the environment files for Patroni nodes
# from a template and a main environment file.

import os
import socket
from string import Template
from pathlib import Path


def create_env_files(local_dir: str = ""):

    # Set the node names - in order
    NODE_NAMES = ["charlemagne", "voluspa", "joyeuse", "kemel", "martel"]
    env_vars = {f"NODE_NAME{i+1}": name for i, name in enumerate(NODE_NAMES)}
    
    # Add the node IPs
    # Load the main environment variables by using the local directory

    if not local_dir:
        # Ask the user for local dir or to exit
        print("No local directory provided. Please provide the path to the local directory containing env.d.")
        print("Press Ctrl+C to exit.")
        print("Or press Enter to use the current directory.")        
        local_dir = input("Please provide the local directory path: ")
        if not local_dir:
            local_dir = Path.cwd()
        else:
            create_env_files(local_dir)
            return
        

    # Retrieve the computer name
    node_name = socket.gethostname()
    env_vars["NODE_NAME"] = node_name.lower()

    # get the local dir
    main_env = os.path.join(local_dir / '.env.d' / 'main.env')
    node_env = os.path.join(local_dir / '.env.d' / f'{node_name.upper()}.env')

    # Read the environment files
    if not os.path.exists(main_env):
        print(f"Main environment file {main_env} does not exist. Exiting.")
        return
    if not os.path.exists(node_env):
        print(f"Node environment file {node_env} does not exist. Exiting.")
        return

    
    for env_file in [node_env, main_env]:
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value

    # Show we've loaded the files in
    print(f"Loaded environment from {node_env} and {main_env}")
    
    # Need to cast them both into a local env file, node first
    output_file_path = local_dir / ".env"
        
    if output_file_path.exists():
        old_content = output_file_path.read_text()
        if old_content != env_vars:
            print(f"[Δ] Updated {output_file_path}")
    else:
        print(f"[+] Created {output_file_path}")
    with open(output_file_path, 'w') as output_file:
        for key, value in env_vars.items():
            output_file.write(f"{key}={value}\n")
    print(f"[✓] Rasputin echo: {node_name.upper()} environment hydrated.")
    
if __name__ == "__main__":
    create_env_files()