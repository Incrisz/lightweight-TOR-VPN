#!/usr/bin/env python3

import subprocess
import sys
import os

# ========= CONFIG =========
TORRC_PATH = "/etc/tor/torrc"
TOR_USER = "debian-tor"   # Default user Tor runs as
TRANS_PORT = "9040"
DNS_PORT = "5353"
# ==========================




def run(cmd, check=True):
    """Run a shell command."""
    print(f"[*] Running: {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def start_tor_tunnel():
    print("[*] Setting up Tor transparent proxy...")

    # 1. Install Tor if not installed
    if subprocess.call("which tor", shell=True) != 0:
        print("[*] Installing Tor...")
        run("apt update && apt install -y tor")

    # 2. Configure torrc
    if not os.path.exists(f"{TORRC_PATH}.bak"):
        run(f"cp {TORRC_PATH} {TORRC_PATH}.bak")
        print(f"[*] Backup of torrc created at {TORRC_PATH}.bak")

    with open(TORRC_PATH, "r+") as f:
        content = f.read()
        if "TransPort" not in content:
            f.write(f"""

# Transparent proxy settings
VirtualAddrNetworkIPv4 10.192.0.0/10
AutomapHostsOnResolve 1
TransPort {TRANS_PORT}
DNSPort {DNS_PORT}
""")
            print("[*] torrc updated for transparent proxy.")

    # Restart Tor
    run("systemctl restart tor")

    # 3. Setup iptables
    print("[*] Setting up iptables rules...")
    run("iptables -F")
    run("iptables -t nat -F")
    run(f"iptables -t nat -A OUTPUT -m owner --uid-owner {TOR_USER} -j RETURN")
    run("iptables -t nat -A OUTPUT -o lo -j RETURN")
    run(f"iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports {TRANS_PORT}")
    run(f"iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports {DNS_PORT}")

    print("[*] Tor tunnel is now active.")

def stop_tor_tunnel():
    print("[*] Stopping Tor transparent proxy...")

    # Restore iptables
    print("[*] Flushing iptables rules...")
    run("iptables -F")
    run("iptables -t nat -F")

    # Restore torrc if backup exists
    if os.path.exists(f"{TORRC_PATH}.bak"):
        run(f"mv {TORRC_PATH}.bak {TORRC_PATH}")
        print("[*] torrc restored from backup.")

    # Restart Tor
    run("systemctl restart tor")

    print("[*] Tor tunnel is now stopped.")

def usage():
    print(f"Usage: {sys.argv[0]} start|stop")
    sys.exit(1)

def main():
    if os.geteuid() != 0:
        print("[-] Please run this script as root (sudo).")
        sys.exit(1)

    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == "start":
        start_tor_tunnel()
    elif sys.argv[1] == "stop":
        stop_tor_tunnel()
    else:
        usage()

if __name__ == "__main__":
    main()
