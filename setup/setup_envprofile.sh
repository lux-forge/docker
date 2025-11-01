#!/bin/bash
# LuxForge EnvProfile Setup Script
# Usage: ./setup/setup_envprofile.sh

PROJECT_ROOT="$(dirname "$(dirname "$(realpath "$0")")")"
VENV_PATH="$PROJECT_ROOT/.luxforge-venv"

echo "[+] Checking for python3-venv"
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "[!] python3-venv not found. Installing..."
    sudo apt update && sudo apt install -y python3-venv
fi

echo "[+] Creating virtual environment at $VENV_PATH"
python3 -m venv "$VENV_PATH"

echo "[+] Activating virtual environment"
source "$VENV_PATH/bin/activate"

echo "[+] Installing dependencies"
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/setup/requirements.txt"

# Ask the user if its a dev environment
read -rp "[?] Is this a development environment? (y/N): " is_dev
if [[ "$is_dev" =~ ^[Yy]$ ]]; then
    echo "[+] Installing development dependencies"
    pip install -r "$PROJECT_ROOT/setup/dev-requirements.txt"
fi

echo "[+] Running trial script"
python "$PROJECT_ROOT/tests/trial_envprofile.py"

if [[ "$is_dev" =~ ^[Yy]$ ]]; then
    echo "[+] Capturing dev requirements"
    pip freeze > "$PROJECT_ROOT/setup/dev-requirements.txt"
else
    echo "[+] Capturing runtime requirements"
    pipreqs "$PROJECT_ROOT/scripts" "$PROJECT_ROOT/tests" --force --savepath "$PROJECT_ROOT/setup/requirements.txt"
fi

echo "[+] Setup complete on $(hostname) at $(date -Iseconds)" >> "$PROJECT_ROOT/logs/setup.log"
echo "[+] To activate the virtual environment, run: source $VENV_PATH/bin/activate"