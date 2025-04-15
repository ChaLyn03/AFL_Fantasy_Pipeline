import os
import sqlite3
import csv
import subprocess
import pytest

DB_PATH = "data/processed/10TeamStats.db"
CSV_PATH = "data/processed/11TeamStats.csv"

@pytest.fixture(scope="module", autouse=True)
def run_full_pipeline():
    print("🔁 Running full pipeline for E2E test")
    try:
        subprocess.run(["python", "scripts/1PlayerScrape.py"], check=True)
        subprocess.run(["python", "scripts/2CoachScrape.py"], check=True)
        subprocess.run(["python", "scripts/5StatCollate.py"], check=True)
        subprocess.run(["python", "scripts/7StatDerivatives.py"], check=True)
        subprocess.run(["python", "scripts/9TeamStats.py"], check=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Pipeline failed at step: {e.cmd}\nError code: {e.returncode}", pytrace=False)

def test_team_db_exists():
    assert os.path.exists(DB_PATH), f"Database {DB_PATH} not created"

def test_team_csv_exists():
    assert os.path.exists(CSV_PATH), f"CSV {CSV_PATH} not created"

def test_db_has_30_unique_players():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT id) FROM team_stats")
    count = cur.fetchone()[0]
    conn.close()
    assert count == 30, f"Expected 30 players, found {count}"

def test_csv_columns_and_rows():
    with open(CSV_PATH, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) > 1, "CSV file is empty or missing header"
    assert len(rows) == 31, f"Expected 1 header + 30 rows, got {len(rows)}"
