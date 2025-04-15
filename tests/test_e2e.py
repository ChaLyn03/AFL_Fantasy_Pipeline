import os
import sqlite3
import pandas as pd
import pytest

# Paths to key output files
DB_TEAM = "data/processed/10TeamStats.db"
CSV_TEAM = "data/processed/11TeamStats.csv"

# --- Fixture: Run pipeline ---
@pytest.fixture(scope="module", autouse=True)
def run_full_pipeline():
    assert os.system("python scripts/1PlayerScrape.py") == 0
    assert os.system("python scripts/2CoachScrape.py") == 0
    assert os.system("python scripts/5StatCollate.py") == 0
    assert os.system("python scripts/7StatDerivatives.py") == 0
    assert os.system("python scripts/9TeamStats.py") == 0

def test_team_db_exists():
    assert os.path.exists(DB_TEAM), "10TeamStats.db missing"

def test_team_csv_exists():
    assert os.path.exists(CSV_TEAM), "11TeamStats.csv missing"

def test_db_has_30_unique_players():
    conn = sqlite3.connect(DB_TEAM)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT id) FROM team_stats")
    unique = cur.fetchone()[0]
    conn.close()
    assert unique == 30, f"Expected 30 players, found {unique}"

def test_csv_columns_and_rows():
    df = pd.read_csv(CSV_TEAM)
    assert len(df) == 30, "CSV does not contain 30 players"
    expected = {"id", "slug", "avg_points", "efficiency"}
    missing = expected - set(df.columns)
    assert not missing, f"Missing columns: {missing}"
