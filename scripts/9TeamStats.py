import requests
import json
import sqlite3
import csv
import os
import sys
import os

DEBUG = os.getenv("DEBUG", "0") == "1"

def debug_print(*args):
    if DEBUG:
        print("DEBUG:", *args)

# --- Configuration for API endpoints and file names ---
TEAM_ENDPOINT = "https://fantasy.afl.com.au/afl_classic/api/teams_classic/show_my"
TRADES_ENDPOINT = "https://fantasy.afl.com.au/afl_classic/api/teams_classic/show_trades"

DERIVATIVE_DB = "data/processed/8StatAll.db"      # Source database with derivative stats from 7DerivativeStats.py
TEAM_DB = "data/processed/10TeamStats.db"         # New database file to be created for team records
TEAM_CSV = "data/processed/11TeamStats.csv"       # CSV output file

headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0",
    # Ensure your cookie is current. Replace with your full valid cookie string if needed.
    "Cookie": ("session=434c5efd3fcacbc3976518ccafb199c0873eb3ee; "
               "__stripe_mid=2d1ae6a9-790d-4280-9824-956f2afdea87f377d4; "
               "_gcl_au=1.1.1883745676.1741221861; "
               "_tt_enable_cookie=1; "
               "_ttp=01JNMEJ5ZDZFD39Y5N6DKFHPHC_.tt.2; "
               "_cb=D54FoYCz2cgMCxN-em; "
               "_hjSessionUser_1941476=eyJpZCI6ImU1NDBkNDRmLThiZTUtNTJmYi1iOWVkLWY2MTAzZWY5MDFhYiIsImNyZWF0ZWQiOjE3NDEyMjE4NjA2MTcsImV4aXN0aW5nIjp0cnVlfQ==; ")
}

debug_print("DEBUG: Starting 9TeamStats.py script.")

# --- Step 1. Retrieve team composition from API ---
debug_print("DEBUG: Retrieving team composition from API endpoint...")
try:
    resp_team = requests.get(TEAM_ENDPOINT, headers=headers)
    resp_team.raise_for_status()
    team_json = resp_team.json()
    debug_print("DEBUG: Team composition API response received:")
    debug_print(json.dumps(team_json, indent=2)[:500] + "\n...")
except Exception as e:
    sys.exit(f"ERROR: Failed to retrieve team composition: {e}")

if team_json.get("success") != 1:
    sys.exit("ERROR: API indicated failure in retrieving team composition. Check your authentication settings.")

team_result = team_json.get("result", {})
lineup = team_result.get("lineup", {})
debug_print("DEBUG: Lineup from API:", lineup)

# Build team member IDs from the lineup
team_member_ids = set()

# Main positions: keys "1", "2", "3", "4"
for pos in ["1", "2", "3", "4"]:
    pos_players = lineup.get(pos, [])
    debug_print(f"DEBUG: Position {pos} players: {pos_players}")
    team_member_ids.update(pos_players)

# Bench players: 'bench' is a dictionary with several keys.
bench = lineup.get("bench", {})
for bench_key, bench_list in bench.items():
    debug_print(f"DEBUG: Bench group '{bench_key}': {bench_list}")
    if isinstance(bench_list, list):
        team_member_ids.update(bench_list)

# Include captain and vice-captain
if lineup.get("captain"):
    team_member_ids.add(lineup["captain"])
    debug_print("DEBUG: Added captain:", lineup["captain"])
if lineup.get("vice_captain"):
    team_member_ids.add(lineup["vice_captain"])
    debug_print("DEBUG: Added vice_captain:", lineup["vice_captain"])

debug_print("DEBUG: Team composition from API (before trades):", team_member_ids)

# --- Step 2. Retrieve pending trades from API and update team member IDs ---
debug_print("DEBUG: Retrieving pending trades from API endpoint...")
try:
    resp_trades = requests.get(TRADES_ENDPOINT, headers=headers)
    resp_trades.raise_for_status()
    trades_json = resp_trades.json()
    debug_print("DEBUG: Trades API response received:")
    debug_print(json.dumps(trades_json, indent=2)[:500] + "\n...")
except Exception as e:
    sys.exit(f"ERROR: Failed to retrieve trades: {e}")

if trades_json.get("success") != 1:
    sys.exit("ERROR: API indicated failure in retrieving trades.")

trades_result = trades_json.get("result", [])
debug_print("DEBUG: Pending trades result:", trades_result)

# For each pending trade, if the old player is in your current team, replace with new_player.
for trade in trades_result:
    old_id = trade.get("old_player_id")
    new_id = trade.get("new_player_id")
    if old_id in team_member_ids:
        debug_print(f"DEBUG: Trade detected. Replacing {old_id} with {new_id}.")
        team_member_ids.remove(old_id)
        team_member_ids.add(new_id)

# Deduplicate
team_member_ids = list(set(team_member_ids))
debug_print("DEBUG: Final team member IDs after processing trades:", team_member_ids)

team_member_ids = list(team_member_ids)

# --- Step 3. Query the derivative database (8StatAll.db) for these player records ---
if not os.path.exists(DERIVATIVE_DB):
    sys.exit(f"ERROR: Source database {DERIVATIVE_DB} not found. Run 7DerivativeStats.py first.")

debug_print(f"DEBUG: Connecting to derivative database: {DERIVATIVE_DB}")
try:
    conn = sqlite3.connect(DERIVATIVE_DB)
    cur = conn.cursor()
    debug_print("DEBUG: Connected to 8StatAll.db successfully.")
except Exception as e:
    sys.exit(f"ERROR: Could not connect to {DERIVATIVE_DB}: {e}")

# Build query with placeholders for team member IDs.
placeholders = ",".join("?" for _ in team_member_ids)
select_query = f"SELECT * FROM player_coach_combined WHERE id IN ({placeholders})"
debug_print("DEBUG: Executing SQL query:", select_query)
try:
    cur.execute(select_query, team_member_ids)
    team_rows = cur.fetchall()
    debug_print(f"DEBUG: Retrieved {len(team_rows)} rows for team members from player_coach_combined.")
except Exception as e:
    sys.exit(f"ERROR: SQL query execution failed: {e}")

# --- Step 4. Create new database (10TeamStats.db) and copy team records ---
debug_print(f"DEBUG: Creating/connecting to new database: {TEAM_DB}")
try:
    conn_team = sqlite3.connect(TEAM_DB)
    cur_team = conn_team.cursor()
    # Attach the source derivative database so we can reference its table schema.
    cur_team.execute(f"ATTACH DATABASE '{DERIVATIVE_DB}' AS source_db")
    debug_print("DEBUG: Attached source_db (8StatAll.db) to new database connection.")
    
    # Create table 'team_stats' in TEAM_DB using the schema from source_db.player_coach_combined.
    cur_team.execute("DROP TABLE IF EXISTS team_stats")
    cur_team.execute("CREATE TABLE team_stats AS SELECT * FROM source_db.player_coach_combined WHERE 0")
    conn_team.commit()
    debug_print("DEBUG: Table 'team_stats' created in TEAM_DB using schema from source_db.")
except Exception as e:
    sys.exit(f"ERROR: Unable to create table in {TEAM_DB}: {e}")

if team_rows:
    num_columns = len(team_rows[0])
    insert_query = f"INSERT INTO team_stats VALUES ({','.join('?' for _ in range(num_columns))})"
    debug_print("DEBUG: Inserting rows into team_stats using query:", insert_query)
    try:
        cur_team.executemany(insert_query, team_rows)
        conn_team.commit()
        debug_print(f"DEBUG: Inserted {len(team_rows)} rows into team_stats in {TEAM_DB}.")
    except Exception as e:
        sys.exit(f"ERROR: Failed to insert rows into {TEAM_DB}: {e}")
else:
    debug_print("WARNING: No team records found to insert into new database.")

# --- Step 5. Export team records to a CSV file (11TeamStats.csv) ---
debug_print(f"DEBUG: Exporting team records to CSV file: {TEAM_CSV}")
try:
    cur.execute("PRAGMA table_info(player_coach_combined)")
    columns_info = cur.fetchall()
    columns = [info[1] for info in columns_info]
    debug_print("DEBUG: Retrieved column names from 8StatAll.db:", columns)
except Exception as e:
    sys.exit(f"ERROR: Could not retrieve table schema: {e}")

try:
    
    with open(TEAM_CSV, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for row in team_rows:
            writer.writerow(row)
    debug_print(f"DEBUG: Exported team records to CSV file: {TEAM_CSV}")
except Exception as e:
    sys.exit(f"ERROR: Failed to write CSV file {TEAM_CSV}: {e}")

# --- Cleanup: Close all database connections ---
conn.close()
conn_team.close()
debug_print("DEBUG: Closed all database connections.")
debug_print("DEBUG: 9TeamStats.py completed successfully.")
