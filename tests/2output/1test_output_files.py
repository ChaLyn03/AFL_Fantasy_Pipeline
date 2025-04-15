import os
import sqlite3
import pandas as pd
import pytest

DB_PATH = "data/processed/10TeamStats.db"
CSV_PATH = "data/processed/11TeamStats.csv"

def test_team_db_exists():
    assert os.path.exists(DB_PATH), "10TeamStats.db does not exist"

def test_team_csv_exists():
    assert os.path.exists(CSV_PATH), "11TeamStats.csv does not exist"

def test_db_has_unique_rows():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM team_stats")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT id) FROM team_stats")
    unique = cur.fetchone()[0]
    conn.close()
    assert total == unique, f"DB has duplicate rows: {total - unique} duplicates"

def test_csv_row_count_matches_db():
    conn = sqlite3.connect(DB_PATH)
    db_df = pd.read_sql_query("SELECT * FROM team_stats", conn)
    csv_df = pd.read_csv(CSV_PATH)
    conn.close()
    assert len(db_df) == len(csv_df), f"Mismatch in row count: DB={len(db_df)}, CSV={len(csv_df)}"

def test_csv_columns_exist():
    df = pd.read_csv(CSV_PATH)
    expected_cols = {"id", "slug", "efficiency", "avg_points"}
    missing = expected_cols - set(df.columns)
    assert not missing, f"Missing columns in CSV: {missing}"
