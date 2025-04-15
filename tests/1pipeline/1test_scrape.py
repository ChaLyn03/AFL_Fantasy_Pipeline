import os
import json
import pytest

PLAYER_JSON = "data/raw/3Player.json"
COACH_JSON = "data/raw/4Coach.json"

@pytest.fixture(scope="module", autouse=True)
def run_scrapers():
    """Run both scrapers before any tests."""
    os.system("python scripts/1PlayerScrape.py")
    os.system("python scripts/2CoachScrape.py")

def test_player_json_exists():
    assert os.path.exists(PLAYER_JSON), "Player JSON not created"

def test_coach_json_exists():
    assert os.path.exists(COACH_JSON), "Coach JSON not created"

def test_player_json_valid():
    with open(PLAYER_JSON, "r") as f:
        data = json.load(f)
    assert isinstance(data, list), "Player JSON should be a list"
    assert len(data) > 0, "Player JSON is empty"

    sample = data[0]
    print("Sample player entry:", sample)
    assert "id" in sample, "Missing 'id' in player entry"
    assert any(k in sample for k in ("slug", "first_name", "last_name")), "Missing name-like keys"

def test_coach_json_valid():
    with open(COACH_JSON, "r") as f:
        data = json.load(f)
    assert isinstance(data, dict), "Coach JSON should be a dict"
    assert len(data) > 0, "Coach JSON is empty"

    sample = next(iter(data.values()))
    print("Sample coach entry:", sample)
    assert "proj_score" in sample, "Coach entry missing 'proj_score'"
    assert isinstance(sample.get("proj_score"), (int, float)), "'proj_score' should be a number"
