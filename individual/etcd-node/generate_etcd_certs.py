#!/usr/bin/env python3

import subprocess
from pathlib import Path
import json

ROOT_DIR = Path("certs")
CA_KEY = ROOT_DIR / "root.key"
CA_CERT = ROOT_DIR / "root.crt"
CONFIG_FILE = ROOT_DIR / "etcd_nodes.json"

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def ensure_root_ca():
    ROOT_DIR.mkdir(exist_ok=True)
    if not CA_KEY.exists() or not CA_CERT.exists():
        print("[+] Generating root CA")
        run(f"openssl genrsa -out {CA_KEY} 4096")
        run(f"openssl req -x509 -new -nodes -key {CA_KEY} -sha256 -days 3650 -out {CA_CERT} -subj '/CN=root-ca'")

def generate_node_cert(name, ip):
    node_dir = ROOT_DIR / name
    node_dir.mkdir(exist_ok=True)
    key = node_dir / f"{name}.key"
    csr = node_dir / f"{name}.csr"
    crt = node_dir / f"{name}.crt"
    extfile = node_dir / "san.cnf"

    extfile.write_text(f"subjectAltName=IP:{ip}\n")

    print(f"[+] Generating cert for {name}")
    run(f"openssl genrsa -out {key} 2048")
    run(f"openssl req -new -key {key} -out {csr} -subj '/CN={name}' -addext 'subjectAltName = IP:{ip}'")
    run(f"openssl x509 -req -in {csr} -CA {CA_CERT} -CAkey {CA_KEY} -CAcreateserial -out {crt} -days 365 -sha256 -extfile {extfile}")

def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")
    with open(CONFIG_FILE) as f:
        return json.load(f)

def main():
    ensure_root_ca()
    node_map = load_config()
    for name, ip in node_map.items():
        generate_node_cert(name, ip)
    print("[✓] All node certs generated and signed.")

if __name__ == "__main__":
    main()