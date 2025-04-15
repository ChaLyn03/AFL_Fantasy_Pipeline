# tests/test_collate.py

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
    expected = {"players", "coaches", "combined"}
    missing = expected - tables
    assert not missing, f"Missing tables: {missing}"

def test_players_table_not_empty(collated_db):
    """Ensure the players table has data."""
    cur = collated_db.cursor()
    cur.execute("SELECT COUNT(*) FROM players")
    count = cur.fetchone()[0]
    assert count > 0, "No player data found"

def test_column_existence(collated_db):
    """Check some key dynamic columns exist."""
    cur = collated_db.cursor()
    cur.execute("PRAGMA table_info(players)")
    columns = {row[1] for row in cur.fetchall()}
    required = {"id", "name", "avg_points"}
    missing = required - columns
    assert not missing, f"Missing columns: {missing}"
