import os
import sqlite3
import pytest

DB_PATH = "data/processed/8StatAll.db"

@pytest.fixture(scope="module")
def enriched_db():
    """Run the derivatives script and return the enriched DB connection."""
    os.system("python scripts/7StatDerivatives.py")
    assert os.path.exists(DB_PATH), "8StatAll.db not created"
    conn = sqlite3.connect(DB_PATH)
    yield conn
    conn.close()

def test_new_columns_exist_player_combined(enriched_db):
    cur = enriched_db.cursor()
    cur.execute("PRAGMA table_info(player_coach_combined)")
    columns = {row[1] for row in cur.fetchall()}
    expected = {"efficiency", "consistency", "recent_trend", "cost_efficiency"}
    missing = expected - columns
    assert not missing, f"Missing player derived columns: {missing}"

def test_values_populated_player_combined(enriched_db):
    cur = enriched_db.cursor()
    cur.execute("SELECT COUNT(*) FROM player_coach_combined WHERE efficiency IS NOT NULL")
    count = cur.fetchone()[0]
    assert count > 0, "efficiency not populated"

    cur.execute("SELECT COUNT(*) FROM player_coach_combined WHERE cost_efficiency IS NOT NULL")
    count = cur.fetchone()[0]
    assert count > 0, "cost_efficiency not populated"

def test_new_columns_exist_coach(enriched_db):
    cur = enriched_db.cursor()
    cur.execute("PRAGMA table_info(coach_raw)")
    columns = {row[1] for row in cur.fetchall()}
    assert "proj_efficiency" in columns, "Missing proj_efficiency in coach_raw"

def test_values_populated_coach(enriched_db):
    cur = enriched_db.cursor()
    cur.execute("SELECT COUNT(*) FROM coach_raw WHERE proj_efficiency IS NOT NULL")
    count = cur.fetchone()[0]
    assert count > 0, "proj_efficiency not populated"
