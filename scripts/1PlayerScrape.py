import requests
import json

# === CONFIG ===
DATA_URL = "https://fantasy.afl.com.au/data/afl/players.json"
OUTPUT_FILE = "3Player.json"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0"
}

# === Fetch and save the data ===
try:
    response = requests.get(DATA_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    with open("data/raw/3Player.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Player data saved to {OUTPUT_FILE}")
except Exception as e:
    print(f"❌ Failed to fetch player data: {e}")
