import sqlite3
import shutil
import os
import sys
import os

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

# --- Copy the fundamental database to create a new one for derivative stats ---
try:
    shutil.copyfile("data/interim/6StatCollate.db", "data/processed/8StatAll.db")
    debug_print(f"Copied {SOURCE_DB} to {DEST_DB}")
except Exception as e:
    sys.exit(f"Error copying database: {e}")

# --- Connect to the new database ---
conn = sqlite3.connect("data/processed/8StatAll.db")
cur = conn.cursor()

def add_column_if_not_exists(table, column, coldef):
    cur.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    if column not in columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}")
        debug_print(f"Added column {column} to {table}")
    else:
        debug_print(f"Column {column} already exists in {table}")

# --- Ensure derivative columns exist in the player_coach_combined table ---
for col, definition in [
    ("efficiency", "REAL"),
    ("consistency", "REAL"),
    ("recent_trend", "REAL"),
    ("cost_efficiency", "REAL")
]:
    add_column_if_not_exists("player_coach_combined", col, definition)

# --- Update each derivative column separately ---

# Update efficiency: total_points per game (guarding against NULL and division by 0)
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

# Update consistency: difference between high_score and low_score
try:
    cur.execute("""
        UPDATE player_coach_combined
        SET consistency = high_score - low_score
    """)
    conn.commit()
    debug_print("Updated consistency in player_coach_combined")
except Exception as e:
    conn.rollback()
    debug_print("Error updating consistency:", e)

# Update recent_trend: difference between last_3_avg and avg_points
try:
    cur.execute("""
        UPDATE player_coach_combined
        SET recent_trend = last_3_avg - avg_points
    """)
    conn.commit()
    debug_print("Updated recent_trend in player_coach_combined")
except Exception as e:
    conn.rollback()
    debug_print("Error updating recent_trend:", e)

# Update cost_efficiency: total_points divided by cost
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

# --- Ensure derivative column exists in the coach_raw table ---
add_column_if_not_exists("coach_raw", "proj_efficiency", "REAL")

# Update proj_efficiency for coach_raw: proj_score divided by draft_selections
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

# --- Close the database connection ---
conn.close()
debug_print("7DerivativeStats.py completed successfully.")
