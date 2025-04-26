#!/bin/bash

# Exit on error
set -e

echo "[*] Flushing all iptables rules..."
sudo iptables -F
sudo iptables -t nat -F

echo "[*] Restoring original Tor configuration if backup exists..."
if [ -f /etc/tor/torrc.bak ]; then
    sudo cp /etc/tor/torrc.bak /etc/tor/torrc
    echo "[+] Restored torrc from backup."
else
    echo "[!] No torrc backup found. Skipping restore."
fi

echo "[*] Restarting Tor service..."
sudo systemctl restart tor

echo "[*] Checking Tor status..."
sleep 3
curl --silent https://check.torproject.org | grep -q "not using Tor" && \
echo "[✅] You are NOT using Tor anymore." || \
echo "[⚠️] You are STILL using Tor!"

echo "[*] Done."
