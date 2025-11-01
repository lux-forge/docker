# !/bin/bash
# LuxForge Update Requirements Script
# Usage: ./scripts/update-requirements.sh

# Ensure we're in the /docker directory
cd /docker || exit 1

echo "[+] Activating virtual environment and updating requirements.txt"

# Activate the virtual environment
source ./.luxforge-venv/bin/activate

# Generate requirements.txt using pipreqs
pipreqs ./scripts ./tests --force --savepath ./setup/requirements.txt