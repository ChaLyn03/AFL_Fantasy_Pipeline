import os
import sqlite3
import pytest

DB_PATH = "data/interim/6StatCollate.db"

@pytest.fixture(scope="module")
def collated_db():
    """Run the collate script and return the database connection."""
    os.system("python scripts/5StatCollate.py")
    assert os.path.exists(DB_PATH), "6StatCollate.db not created"
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()

def test_tables_exist(collated_db):
    cur = collated_db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    expected = {"player_raw", "coach_raw", "player_coach_combined"}
    missing = expected - tables
    assert not missing, f"Missing tables: {missing}"

def test_player_table_not_empty(collated_db):
    cur = collated_db.cursor()
    cur.execute("SELECT COUNT(*) FROM player_raw")
    count = cur.fetchone()[0]
    assert count > 0, "player_raw table is empty"

def test_coach_table_not_empty(collated_db):
    cur = collated_db.cursor()
    cur.execute("SELECT COUNT(*) FROM coach_raw")
    count = cur.fetchone()[0]
    assert count > 0, "coach_raw table is empty"

def test_player_columns_exist(collated_db):
    cur = collated_db.cursor()
    cur.execute("PRAGMA table_info(player_raw)")
    columns = {row[1] for row in cur.fetchall()}
    expected = {"id", "slug", "avg_points", "cost"}
    missing = expected - columns
    assert not missing, f"Missing player columns: {missing}"

def test_coach_columns_exist(collated_db):
    cur = collated_db.cursor()
    cur.execute("PRAGMA table_info(coach_raw)")
    columns = {row[1] for row in cur.fetchall()}
    expected = {"id", "proj_score", "last_3_proj_avg", "break_even"}
    missing = expected - columns
    assert not missing, f"Missing coach columns: {missing}"

def test_player_ids_unique(collated_db):
    cur = collated_db.cursor()
    cur.execute("SELECT id, COUNT(*) FROM player_raw GROUP BY id HAVING COUNT(*) > 1")
    duplicates = cur.fetchall()
    assert not duplicates, f"Duplicate player IDs found: {duplicates}"
