#!/bin/bash

set -e

# ========= CONFIG =========
TORRC_PATH="/etc/tor/torrc"
TOR_USER="debian-tor" # Default user Tor runs as on Debian/Ubuntu
TRANS_PORT="9040"
DNS_PORT="5353"
# ==========================

echo "[*] Starting full Tor transparent proxy setup..."

# 1. Install Tor if not installed
install_tor() {
  if ! command -v tor >/dev/null 2>&1; then
    echo "[*] Installing Tor..."
    apt update
    apt install -y tor
  else
    echo "[*] Tor already installed."
  fi
}

# 2. Configure torrc
configure_torrc() {
  echo "[*] Configuring Tor..."

  # Backup existing torrc
  if [ ! -f "${TORRC_PATH}.bak" ]; then
    cp "$TORRC_PATH" "${TORRC_PATH}.bak"
    echo "[*] Backup of torrc created at ${TORRC_PATH}.bak"
  fi

  # Append transparent proxy settings if not already set
  grep -q "TransPort $TRANS_PORT" "$TORRC_PATH" || echo "
# Transparent proxy settings
VirtualAddrNetworkIPv4 10.192.0.0/10
AutomapHostsOnResolve 1
TransPort $TRANS_PORT
DNSPort $DNS_PORT
" >> "$TORRC_PATH"

  echo "[*] Restarting Tor service..."
  systemctl restart tor
}

# 3. Set up iptables rules
setup_iptables() {
  echo "[*] Setting up iptables rules..."

  # Flush old rules
  iptables -F
  iptables -t nat -F

  # Allow Tor user to make direct connections
  iptables -t nat -A OUTPUT -m owner --uid-owner $TOR_USER -j RETURN

  # Allow loopback
  iptables -t nat -A OUTPUT -o lo -j RETURN

  # Redirect all TCP SYN packets to Tor's TransPort
  iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $TRANS_PORT

  # Redirect DNS requests to Tor's DNSPort
  iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports $DNS_PORT

  echo "[*] iptables rules applied."
}

# 4. (Optional) Save iptables rules to survive reboot
save_iptables() {
  echo "[*] Saving iptables rules..."

  apt install -y iptables-persistent

  netfilter-persistent save
  netfilter-persistent reload

  echo "[*] iptables rules saved and will persist after reboot."
}

# 5. Run everything
install_tor
configure_torrc
setup_iptables
save_iptables

echo "[*] Tor transparent proxy setup complete!"
echo "[*] Your traffic is now being tunneled through Tor."
