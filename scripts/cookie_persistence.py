import os
import json
import requests
from pathlib import Path

# -------------- Configuration --------------
# List all protected endpoints here
ENDPOINTS = [
    "https://fantasy.afl.com.au/data/afl/cgmbanner.json",
    "https://fantasy.afl.com.au/data/afl/coach/players.json",
    "https://fantasy.afl.com.au/data/afl/countries.json",
    "https://fantasy.afl.com.au/data/afl/matches_fin.json",
    "https://fantasy.afl.com.au/data/afl/players.json",
    "https://fantasy.afl.com.au/data/afl/players_fin.json",
    "https://fantasy.afl.com.au/data/afl/preseason.json",
    "https://fantasy.afl.com.au/data/afl/rounds.json",
    "https://fantasy.afl.com.au/data/afl/squads.json",
    "https://fantasy.afl.com.au/data/afl/squads_fin.json",
    "https://fantasy.afl.com.au/data/afl/venues.json",
]

# Path to a JSON file containing your exported session cookies, e.g.:
# {
#   "session": "434c5efd3fcacbc3976518ccafb199c0873eb3ee",
#   "__stripe_mid": "...",
#   "other_cookie": "..."
# }
COOKIES_FILE = "cookies.json"

# File to persist ETag & Last-Modified metadata
METADATA_FILE = "fetch_metadata.json"

# Directory to save raw JSON responses
RAW_DATA_DIR = Path("raw_data")


# -------------- Helper Functions --------------
def load_cookies(path: str) -> dict:
    """Load cookies from a JSON file exported from your browser."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cookie file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_metadata(path: str) -> dict:
    """Load previously stored ETag/Last-Modified info."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metadata(path: str, metadata: dict):
    """Persist ETag/Last-Modified info for next run."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def fetch_endpoint(session: requests.Session, url: str, metadata: dict):
    """Fetch a URL with conditional headers, save JSON on change."""
    headers = {}
    meta = metadata.get(url, {})
    if meta.get("etag"):
        headers["If-None-Match"] = meta["etag"]
    if meta.get("last_modified"):
        headers["If-Modified-Since"] = meta["last_modified"]
    
    resp = session.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        # Save raw JSON
        RAW_DATA_DIR.mkdir(exist_ok=True)
        filename = url.split("/")[-1]
        file_path = RAW_DATA_DIR / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        # Update metadata
        metadata[url] = {
            "etag": resp.headers.get("ETag"),
            "last_modified": resp.headers.get("Last-Modified")
        }
        print(f"[200] Saved updated data for {url}")
    elif resp.status_code == 304:
        print(f"[304] No change: {url}")
    else:
        print(f"[{resp.status_code}] Failed to fetch {url}")


# -------------- Main Execution --------------
def main():
    # 1. Create a session and load cookies
    session = requests.Session()
    cookies = load_cookies(COOKIES_FILE)
    session.cookies.update(cookies)

    # 2. Load metadata
    metadata = load_metadata(METADATA_FILE)

    # 3. Iterate endpoints
    for url in ENDPOINTS:
        fetch_endpoint(session, url, metadata)

    # 4. Persist metadata for next run
    save_metadata(METADATA_FILE, metadata)


if __name__ == "__main__":
    main()
