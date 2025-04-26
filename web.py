#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
import subprocess
import os

app = FastAPI()

# ========= CONFIG =========
TORRC_PATH = "/etc/tor/torrc"
TOR_USER = "debian-tor"
TRANS_PORT = "9040"
DNS_PORT = "5353"
STATE_FILE = "/tmp/tor_tunnel_state"
# ==========================

def run(cmd, check=True):
    """Run a shell command."""
    print(f"[*] Running: {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def start_tor_tunnel():
    """Start Tor tunneling."""
    if subprocess.call("which tor", shell=True) != 0:
        run("apt update && apt install -y tor")

    if not os.path.exists(f"{TORRC_PATH}.bak"):
        run(f"cp {TORRC_PATH} {TORRC_PATH}.bak")

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

    run("systemctl restart tor")

    run("iptables -F")
    run("iptables -t nat -F")
    run(f"iptables -t nat -A OUTPUT -m owner --uid-owner {TOR_USER} -j RETURN")
    run("iptables -t nat -A OUTPUT -o lo -j RETURN")
    run(f"iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports {TRANS_PORT}")
    run(f"iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports {DNS_PORT}")

    with open(STATE_FILE, "w") as f:
        f.write("on")

def stop_tor_tunnel():
    """Stop Tor tunneling."""
    run("iptables -F")
    run("iptables -t nat -F")

    if os.path.exists(f"{TORRC_PATH}.bak"):
        run(f"mv {TORRC_PATH}.bak {TORRC_PATH}")

    run("systemctl restart tor")

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

def is_tor_running():
    """Check if Tor tunnel is active."""
    return os.path.exists(STATE_FILE)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Render the main page."""
    tor_running = is_tor_running()
    button_text = "🛑 STOP" if tor_running else "🚀 START"
    button_class = "on" if tor_running else "off"

    return f"""
    <html>
    <head>
        <title>Tor Tunnel Controller</title>
        <style>
            body {{
                background: linear-gradient(to right, #141e30, #243b55);
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }}
            h1 {{
                font-size: 3em;
                margin-bottom: 30px;
                text-shadow: 2px 2px 5px #000;
            }}
            form {{
                margin: 15px;
            }}
            button {{
                font-size: 2em;
                padding: 20px 40px;
                border: none;
                border-radius: 15px;
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .on {{
                background: #00c6ff;
                color: white;
                box-shadow: 0 4px 20px rgba(0, 198, 255, 0.8);
            }}
            .on:hover {{
                background: #0072ff;
                transform: scale(1.05);
                box-shadow: 0 6px 25px rgba(0, 114, 255, 1);
            }}
            .off {{
                background: grey;
                color: white;
                box-shadow: 0 2px 10px rgba(100, 100, 100, 0.6);
            }}
            .off:hover {{
                background: darkgrey;
                transform: scale(1.05);
            }}
            footer {{
                position: absolute;
                bottom: 10px;
                font-size: 0.9em;
                color: #aaa;
            }}
        </style>
    </head>
    <body>
        <h1>🚀 Tor Tunnel -> Developed by Incrisz </h1>

        <form action="/toggle" method="post">
            <button class="{button_class}">{button_text}</button>
        </form>

        <footer>Developed by Incrisz</footer>
    </body>
    </html>
    """

@app.post("/toggle")
async def toggle():
    """Toggle tunnel on/off."""
    if is_tor_running():
        stop_tor_tunnel()
    else:
        start_tor_tunnel()
    return RedirectResponse(url="/", status_code=303)
