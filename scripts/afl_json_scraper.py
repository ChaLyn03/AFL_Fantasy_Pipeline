import os
import json
import requests
from datetime import datetime
from pathlib import Path

# 🔧 Settings
BASE_DIR = Path("data/store_json")
BASE_DIR.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

# 🌐 Endpoints
endpoints = {
    "players": "https://fantasy.afl.com.au/data/afl/players.json",
    "coach_players": "https://fantasy.afl.com.au/data/afl/coach/players.json",
    "rounds": "https://fantasy.afl.com.au/data/afl/rounds.json",
    "squads": "https://fantasy.afl.com.au/data/afl/squads.json",
    "venues": "https://fantasy.afl.com.au/data/afl/venues.json",
    "players_opp_stats": "https://fantasy.afl.com.au/data/afl/stats/players_opponents_stats.json",
    "players_venue_stats": "https://fantasy.afl.com.au/data/afl/stats/players_venues_stats.json",
    "snapshot": "https://fantasy.afl.com.au/afl_classic/api/teams_classic/snapshot",
    "show_my": "https://fantasy.afl.com.au/afl_classic/api/teams_classic/show_my",
}

# 📥 Download JSON files
downloaded_files = {}
for name, url in endpoints.items():
    try:
        response = requests.get(url)
        response.raise_for_status()
        filename = f"{name}_{timestamp}.json"
        filepath = BASE_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2)
        downloaded_files[name] = filepath
        print(f"✔ Downloaded: {name}")
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")

# ✅ Check for 'players' before continuing
if "players" not in downloaded_files:
    print("⚠️  'players.json' was not downloaded successfully. Exiting.")
    exit()

# 👤 Now parse player IDs from downloaded players.json
players_path = downloaded_files["players"]
with open(players_path, "r", encoding="utf-8") as f:
    players_data = json.load(f)

PLAYER_STATS_DIR = BASE_DIR / f"player_stats_{timestamp}"
PLAYER_STATS_DIR.mkdir(parents=True, exist_ok=True)

for player in players_data:
    player_id = player.get("id")
    if not player_id:
        continue
    url = f"https://fantasy.afl.com.au/data/afl/stats/players/{player_id}.json"
    try:
        res = requests.get(url)
        res.raise_for_status()
        with open(PLAYER_STATS_DIR / f"{player_id}.json", "w") as f:
            json.dump(res.json(), f, indent=2)
        print(f"📄 Player {player_id} stats downloaded")
    except Exception as e:
        print(f"⚠️  Failed for player {player_id}: {e}")
