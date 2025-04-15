import sqlite3
import shutil
import os
import sys

DEBUG = os.getenv("DEBUG", "0") == "1"

def debug_print(*args):
    if DEBUG:
        print("DEBUG:", *args)

# --- Configuration ---
SOURCE_DB = "data/interim/6StatCollate.db"
DEST_DB = "data/processed/8StatAll.db"

# Check that the source database exists
if not os.path.exists(SOURCE_DB):
    sys.exit(f"Source database {SOURCE_DB} does not exist.")

# --- Copy the source DB to create a new enriched version ---
try:
    shutil.copyfile(SOURCE_DB, DEST_DB)
    debug_print(f"Copied {SOURCE_DB} to {DEST_DB}")
except Exception as e:
    sys.exit(f"Error copying database: {e}")

# --- Connect to the new database ---
conn = sqlite3.connect(DEST_DB)
cur = conn.cursor()

def add_column_if_not_exists(table, column, coldef):
    cur.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    if column not in columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}")
        debug_print(f"Added column {column} to {table}")
    else:
        debug_print(f"Column {column} already exists in {table}")

# --- Add derivative columns to player_coach_combined ---
for col, definition in [
    ("efficiency", "REAL"),
    ("custom_consistency", "REAL"),
    ("recent_trend", "REAL"),
    ("cost_efficiency", "REAL")
]:
    add_column_if_not_exists("player_coach_combined", col, definition)

# --- Derivative calculations ---

# 1. Efficiency = total_points / games_played
try:
    cur.execute("""
        UPDATE player_coach_combined
        SET efficiency = CASE
            WHEN games_played IS NOT NULL AND games_played > 0 THEN total_points * 1.0 / games_played
            ELSE 0
        END
    """)
    conn.commit()
    debug_print("Updated efficiency in player_coach_combined")
except Exception as e:
    conn.rollback()
    debug_print("Error updating efficiency:", e)

# 2. Custom consistency = high_score - low_score
try:
    cur.execute("""
        UPDATE player_coach_combined
        SET custom_consistency = CASE
            WHEN high_score IS NOT NULL AND low_score IS NOT NULL THEN high_score - low_score
            ELSE NULL
        END
    """)
    conn.commit()
    debug_print("Updated custom_consistency in player_coach_combined")
except Exception as e:
    conn.rollback()
    debug_print("Error updating custom_consistency:", e)

# 3. Recent trend = last_3_avg - avg_points
try:
    cur.execute("""
        UPDATE player_coach_combined
        SET recent_trend = CASE
            WHEN last_3_avg IS NOT NULL AND avg_points IS NOT NULL THEN last_3_avg - avg_points
            ELSE NULL
        END
    """)
    conn.commit()
    debug_print("Updated recent_trend in player_coach_combined")
except Exception as e:
    conn.rollback()
    debug_print("Error updating recent_trend:", e)

# 4. Cost efficiency = total_points / cost
try:
    cur.execute("""
        UPDATE player_coach_combined
        SET cost_efficiency = CASE
            WHEN cost IS NOT NULL AND cost > 0 THEN total_points * 1.0 / cost
            ELSE 0
        END
    """)
    conn.commit()
    debug_print("Updated cost_efficiency in player_coach_combined")
except Exception as e:
    conn.rollback()
    debug_print("Error updating cost_efficiency:", e)

# --- Coach projections: proj_efficiency = proj_score / draft_selections ---
add_column_if_not_exists("coach_raw", "proj_efficiency", "REAL")

try:
    cur.execute("""
        UPDATE coach_raw
        SET proj_efficiency = CASE
            WHEN draft_selections IS NOT NULL AND draft_selections > 0 THEN proj_score * 1.0 / draft_selections
            ELSE 0
        END
    """)
    conn.commit()
    debug_print("Updated proj_efficiency in coach_raw")
except Exception as e:
    conn.rollback()
    debug_print("Error updating proj_efficiency:", e)

# --- Close DB ---
conn.close()
debug_print("7StatDerivatives.py completed successfully.")
