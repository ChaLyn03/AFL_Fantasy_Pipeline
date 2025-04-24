from pathlib import Path
from datetime import datetime
import json

# Create directory if it doesn't exist
BASE_DIR = Path("data/store_json")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Timestamped filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"cookie_headers_{timestamp}.txt"
filepath = BASE_DIR / filename

# Content to write
content = """
Session Cookie:
session=434c5efd3fcacbc3976518ccafb199c0873eb3ee

User-Agent:
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36

Example GET Request:
GET https://fantasy.afl.com.au/afl_classic/api/teams_classic/show_my
GET https://fantasy.afl.com.au/afl_classic/api/teams_classic/snapshot

Headers:
accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br, zstd
accept-language: en-GB,en-US;q=0.9,en;q=0.8
referer: https://fantasy.afl.com.au/classic/player/george-hewett
sec-ch-ua: "Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
"""

# Write to file
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

filepath.name

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 🔧 Settings
BASE_DIR = Path("data/store_json")
BASE_DIR.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

# 🌐 Endpoints (authenticated ones)
endpoints = {
    "snapshot": "https://fantasy.afl.com.au/afl_classic/api/teams_classic/snapshot",
    "show_my": "https://fantasy.afl.com.au/afl_classic/api/teams_classic/show_my",
}

# 🍪 Session cookie (fill in your real session cookie string here)
SESSION_COOKIE = "434c5efd3fcacbc3976518ccafb199c0873eb3ee"

# 🧠 Request headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}

# 🍪 Attach cookie as dict for `requests`
cookies = {
    "session": SESSION_COOKIE
}

# 📥 Download JSON files
downloaded_files = {}
for name, url in endpoints.items():
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        filename = f"{name}_{timestamp}.json"
        filepath = BASE_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2)
        downloaded_files[name] = filepath
        print(f"✔ Downloaded: {name}")
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")

