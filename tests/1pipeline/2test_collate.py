import os
import sqlite3
import pytest

DB_PATH = "data/interim/6StatCollate.db"

@pytest.fixture(scope="module")
def collated_db():
    """Run the collate script before tests."""
    os.system("python scripts/5StatCollate.py")
    assert os.path.exists(DB_PATH), "Database not created"
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()

def test_tables_exist(collated_db):
    """Check expected tables exist in the database."""
    cur = collated_db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    expected = {"player_raw", "coach_raw", "player_coach_combined"}
    missing = expected - tables
    assert not missing, f"Missing tables: {missing}"

def test_player_raw_not_empty(collated_db):
    """Ensure the player_raw table has data."""
    cur = collated_db.cursor()
    cur.execute("SELECT COUNT(*) FROM player_raw")
    count = cur.fetchone()[0]
    assert count > 0, "No player data found"

def test_column_existence_in_player_raw(collated_db):
    """Check some key dynamic columns exist in player_raw."""
    cur = collated_db.cursor()
    cur.execute("PRAGMA table_info(player_raw)")
    columns = {row[1] for row in cur.fetchall()}
    required = {"id", "name", "avg_points"}
    missing = required - columns
    assert not missing, f"Missing columns: {missing}"
