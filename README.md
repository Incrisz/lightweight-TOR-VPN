# lightweight-TOR-VPN


## Make it executable

sudo chmod +x start-vpn.py

## Run it as root:

sudo ./start-vpn.py start   # to start tunneling through Tor

sudo ./start-vpn.py stop    # to stop tunneling through Tor

## Test via terminal

curl https://check.torproject.org

## TEst via browser
https://check.torproject.org




# Tor Tunnel Controller

A simple web interface to toggle full system traffic tunneling through Tor.  
Developed by Incrisz.

---

## Web Setup Instructions

### 1. Become Superuser
```bash

sudo su

# 2. Install Python Virtual Environment

apt install python3.12-venv -y

# 3. Create and Activate a Virtual Environment
python3 -m venv myenv
source myenv/bin/activate

# 4. Install Required Python Packages
pip install numpy pandas matplotlib scipy openpyxl streamlit scikit-learn reportlab pyproj folium streamlit-folium fastapi uvicorn

# 5. Run the Application
uvicorn web:app --host 0.0.0.0 --port 8000
