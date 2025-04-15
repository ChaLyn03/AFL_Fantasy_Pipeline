import os
import sqlite3
import pandas as pd
import pytest

DB_PATH = "data/processed/10TeamStats.db"
CSV_PATH = "data/processed/11TeamStats.csv"

@pytest.fixture(scope="module")
def team_outputs():
    """Run team extraction and return both DB + CSV info."""
    os.system("python scripts/9TeamStats.py")
    assert os.path.exists(DB_PATH), "10TeamStats.db not created"
    assert os.path.exists(CSV_PATH), "11TeamStats.csv not created"
    return True  # Just a marker for dependency

def test_db_structure(team_outputs):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert "team_stats" in tables, "Missing 'team_stats' table"

    cur.execute("SELECT COUNT(*) FROM team_stats")
    count = cur.fetchone()[0]
    assert count >= 30, f"Expected at least 30 players, found {count}"
    conn.close()

def test_csv_output(team_outputs):
    df = pd.read_csv(CSV_PATH)
    assert not df.empty, "CSV is empty"
    assert "id" in df.columns, "Missing 'id' in CSV"
    assert "efficiency" in df.columns, "Missing derived stat 'efficiency' in CSV"

def test_consistency_between_db_and_csv(team_outputs):
    conn = sqlite3.connect(DB_PATH)
    db_df = pd.read_sql_query("SELECT * FROM team_stats", conn)
    csv_df = pd.read_csv(CSV_PATH)
    assert len(db_df) == len(csv_df), "DB and CSV row counts do not match"
    conn.close()
