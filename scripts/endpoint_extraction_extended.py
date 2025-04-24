import os
import json
import requests
from http.cookiejar import MozillaCookieJar

# === CONFIGURATION ===
BASE_JSON_URL = "https://fantasy.afl.com.au/data/afl/"
COOKIES_TXT   = "cookies.txt"   # Netscape-format cookies
OUTPUT_DIR    = "raw_data"

# Static JSON and Private endpoints to fetch
static_json_endpoints = [
    "players.json",
    "coach/players.json",
    "stats/all.json",
    "stats/players_venues_stats.json",
    "stats/players_opponents_stats.json",
    "rounds.json",
    "leagues_classic/show_my" 
]

static_private_endpoints = [
    "players/favourites",
    "players/add_to_favourites",
    "players/remove_from_favourites"
]

# === SESSION SETUP ===
jar = MozillaCookieJar()
jar.load(COOKIES_TXT, ignore_discard=True, ignore_expires=True)
session = requests.Session()
session.cookies = jar
session.headers.update({
    "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept":           "application/json, text/plain, */*",
    "Origin":           "https://fantasy.afl.com.au",
    "Referer":          "https://fantasy.afl.com.au/classic/team",
    "X-Requested-With": "XMLHttpRequest"
})

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === FETCH FUNCTION ===
def fetch_and_save(url, out_path):
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✔ Saved {out_path}")
        return data
    else:
        print(f"✖ Failed {url} [{resp.status_code}]")
        return None

# === FETCH STATIC JSON ===
print("\n--- Fetching static JSON endpoints ---")
for ep in static_json_endpoints:
    url = BASE_JSON_URL + ep
    out = os.path.join(OUTPUT_DIR, *ep.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fetch_and_save(url, out)

# === FETCH STATIC PRIVATE ===
print("\n--- Fetching static Private endpoints ---")
for ep in static_private_endpoints:
    url = BASE_JSON_URL + ep
    out = os.path.join(OUTPUT_DIR, *ep.split("/")) + ".json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fetch_and_save(url, out)

# === LOAD PLAYERS FOR DYNAMIC ===
players_data = None
with open(os.path.join(OUTPUT_DIR, "players.json"), "r", encoding="utf-8") as f:
    players_data = json.load(f)

# Handle list vs dict
if isinstance(players_data, dict) and "players" in players_data:
    player_list = players_data["players"]
elif isinstance(players_data, list):
    player_list = players_data
else:
    player_list = []

player_ids = [p.get("id") for p in player_list if isinstance(p, dict) and "id" in p]

# === FETCH PER-PLAYER STATS ===
print("\n--- Fetching per-player match stats ---")
for pid in player_ids:
    path = f"stats/players/{pid}.json"
    url = BASE_JSON_URL + path
    out = os.path.join(OUTPUT_DIR, "stats", "players", f"{pid}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fetch_and_save(url, out)

# === LOAD ROUNDS FOR DYNAMIC ===
rounds_data = None
with open(os.path.join(OUTPUT_DIR, "rounds.json"), "r", encoding="utf-8") as f:
    rounds_data = json.load(f)

# Handle list vs dict
if isinstance(rounds_data, dict) and "rounds" in rounds_data:
    round_list = rounds_data["rounds"]
elif isinstance(rounds_data, list):
    round_list = rounds_data
else:
    round_list = []

# Determine round IDs field
round_ids = []
for r in round_list:
    if isinstance(r, dict):
        round_ids.append(r.get("round") or r.get("id"))
    elif isinstance(r, int):
        round_ids.append(r)

# === FETCH PER-ROUND STATS ===
print("\n--- Fetching all matches per round ---")
for rid in round_ids:
    if rid is None:
        continue
    path = f"stats/{rid}.json"
    url = BASE_JSON_URL + path
    out = os.path.join(OUTPUT_DIR, "stats", f"{rid}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fetch_and_save(url, out)

print("\nDone! All static and dynamic endpoints scraped into raw_data/")
