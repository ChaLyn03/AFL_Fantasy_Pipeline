import requests
import json
import os

DEBUG = os.getenv("DEBUG", "0") == "1"

def debug_print(*args):
    if DEBUG:
        print("DEBUG:", *args)

# === CONFIG ===
DATA_URL = "https://fantasy.afl.com.au/data/afl/coach/players.json"
OUTPUT_FILE = "4Coach.json"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0"
}

# === Fetch and save the data ===
try:
    response = requests.get(DATA_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    with open("data/raw/4Coach.json", "w") as f:
        json.dump(data, f, indent=2)
    debug_print(f"✅ Coach data saved to {OUTPUT_FILE}")
except Exception as e:
    debug_print(f"❌ Failed to fetch coach data: {e}")
