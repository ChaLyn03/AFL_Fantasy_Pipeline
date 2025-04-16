import os
import json
import requests
from urllib.parse import urlparse

# === Setup ===
STORAGE_DIR = "data/json_storage"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fantasy.afl.com.au/"
}

# === Provided known-good URLs ===
ENDPOINTS = [
    "https://fantasy.afl.com.au/data/afl/stats/players_opponents_stats.json",
    "https://fantasy.afl.com.au/data/afl/stats/players_venues_stats.json",
    "https://fantasy.afl.com.au/data/afl/rounds.json",
    "https://fantasy.afl.com.au/data/afl/stats/players/1001195.json"
]

# === Utility: Save JSON response ===
def save_json_from_url(url: str):
    try:
        print(f"🔽 Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # Create a folder structure that mimics the path in the URL
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        save_path = os.path.join(STORAGE_DIR, path)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Saved: {save_path}")
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")

# === Run Download ===
for endpoint in ENDPOINTS:
    save_json_from_url(endpoint)
