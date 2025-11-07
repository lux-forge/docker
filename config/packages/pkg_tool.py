#!/usr/bin/env python3
import subprocess
import os

EXPORT_PATH = "/docker/helper_scripts/packages"
os.makedirs(EXPORT_PATH, exist_ok=True)

def export_package_list():
    print("[+] Exporting system packages...")
    subprocess.run(["dpkg", "--get-selections"], stdout=open(f"{EXPORT_PATH}/packages.list", "w"), check=True)
    subprocess.run(["apt-mark", "showmanual"], stdout=open(f"{EXPORT_PATH}/manual-packages.list", "w"), check=True)
    subprocess.run(["dpkg-query", "-W", "-f=${Package}=${Version}\n"], stdout=open(f"{EXPORT_PATH}/packages-with-versions.txt", "w"), check=True)
    print("[✓] System package export complete.")

def export_python_packages():
    venv_pip = os.path.join(os.getcwd(), ".luxforge-venv", "bin", "pip")
    if not os.path.exists(venv_pip):
        print("[!] .luxforge-venv not found. Activate or create it first.")
        return
    print("[+] Exporting Python packages from .luxforge-venv...")
    subprocess.run([venv_pip, "freeze"], stdout=open(f"{EXPORT_PATH}/python-requirements.txt", "w"), check=True)
    print("[✓] Python package export complete.")

def install_packages():
    path = f"{EXPORT_PATH}/manual-packages.list"
    if not os.path.exists(path):
        print("[!] Package list not found. Run export first.")
        return
    print("[+] Installing system packages...")
    with open(path) as f:
        packages = [line.strip() for line in f if line.strip()]
    subprocess.run(["sudo", "apt", "update"], check=True)
    subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
    print("[✓] System package installation complete.")

def install_python_packages():
    req_path = f"{EXPORT_PATH}/python-requirements.txt"
    venv_pip = os.path.join(os.getcwd(), ".luxforge-venv", "bin", "pip")
    if not os.path.exists(req_path):
        print("[!] Python requirements file not found. Run export first.")
        return
    if not os.path.exists(venv_pip):
        print("[!] .luxforge-venv not found. Activate or create it first.")
        return
    print("[+] Installing Python packages into .luxforge-venv...")
    subprocess.run([venv_pip, "install", "-r", req_path], check=True)
    print("[✓] Python package installation complete.")

def download_offline_cache():
    input_path = f"{EXPORT_PATH}/manual-packages.list"
    output_dir = os.path.join(EXPORT_PATH, "offline-cache")
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(input_path):
        print("[!] Package list not found. Run export first.")
        return
    print("[+] Downloading offline cache...")
    with open(input_path) as f:
        packages = [line.strip() for line in f if line.strip()]
    for pkg in packages:
        subprocess.run(["sudo", "apt-get", "download", pkg], cwd=output_dir, check=True)
    print("[✓] Offline cache downloaded.")

def main():
    while True:
        print("\n=== Package Tool Menu ===")
        print("1. Export system packages")
        print("2. Export Python packages from .luxforge-venv")
        print("3. Install system packages")
        print("4. Install Python packages into .luxforge-venv")
        print("5. Download offline cache")
        print("x. Exit")
        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            export_package_list()
        elif choice == "2":
            export_python_packages()
        elif choice == "3":
            install_packages()
        elif choice == "4":
            install_python_packages()
        elif choice == "5":
            download_offline_cache()
        elif choice == "x":
            print("Exiting.")
            break
        else:
            print("[!] Invalid selection.")

if __name__ == "__main__":
    main()