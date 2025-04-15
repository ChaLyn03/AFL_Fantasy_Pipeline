import json
import sqlite3
import os

DEBUG = os.getenv("DEBUG", "0") == "1"

def debug_print(*args):
    if DEBUG:
        print("DEBUG:", *args)

# --- Load JSON Files ---
with open("data/raw/3Player.json") as f:
    players = json.load(f)

with open("data/raw/4Coach.json") as f:
    coaches = json.load(f)

# --- Build dynamic keys ---
price_rounds = set()
score_rounds = set()
rank_rounds = set()
vs_rounds = set()
transfer_rounds = set()

proj_score_rounds = set()
proj_price_rounds = set()
be_rounds = set()
be_pct_rounds = set()
coach_transfer_rounds = set()

for p in players:
    s = p.get("stats", {})
    price_rounds.update(s.get("prices", {}).keys())
    score_rounds.update(s.get("scores", {}).keys())
    rank_rounds.update(s.get("ranks", {}).keys())
    vs_rounds.update(s.get("career_avg_vs", {}).keys())
    transfer_rounds.update(s.get("transfers", {}).keys())

for c in coaches.values():
    proj_score_rounds.update(c.get("proj_scores", {}).keys())
    proj_price_rounds.update(c.get("proj_prices", {}).keys())
    be_rounds.update(c.get("break_evens", {}).keys())
    be_pct_rounds.update(c.get("be_pct", {}).keys())
    coach_transfer_rounds.update(c.get("transfers", {}).keys())

# Sort rounds for consistent column order
def sort_keys(keys):
    return sorted(keys, key=lambda x: int(x))

price_rounds = sort_keys(price_rounds)
score_rounds = sort_keys(score_rounds)
rank_rounds = sort_keys(rank_rounds)
vs_rounds = sort_keys(vs_rounds)
transfer_rounds = sort_keys(transfer_rounds)

proj_score_rounds = sort_keys(proj_score_rounds)
proj_price_rounds = sort_keys(proj_price_rounds)
be_rounds = sort_keys(be_rounds)
be_pct_rounds = sort_keys(be_pct_rounds)
coach_transfer_rounds = sort_keys(coach_transfer_rounds)

# Connect to DB
conn = sqlite3.connect("data/interim/6StatCollate.db")
cur = conn.cursor()

# === Reset tables ===
cur.execute("DROP TABLE IF EXISTS player_raw")
cur.execute("DROP TABLE IF EXISTS coach_raw")
cur.execute("DROP TABLE IF EXISTS player_coach_combined")

# --- Build player_raw CREATE TABLE ---
player_fields = [
    "id INTEGER PRIMARY KEY",
    "name TEXT",
    "slug TEXT",
    "dob TEXT",
    "squad_id INTEGER",
    "cost INTEGER",
    "status TEXT",
    "pos1 INTEGER", "pos2 INTEGER",
    "is_bye INTEGER",
    "locked INTEGER",
]

player_fields += [f"price_r{r} INTEGER" for r in price_rounds]
player_fields += [f"score_r{r} INTEGER" for r in score_rounds]
player_fields += [f"rank_r{r} INTEGER" for r in rank_rounds]

for r in transfer_rounds:
    player_fields.append(f"trans_r{r}_in INTEGER")
    player_fields.append(f"trans_r{r}_out INTEGER")

player_fields += [
    "season_rank INTEGER",
    "games_played INTEGER",
    "total_points INTEGER",
    "avg_points REAL",
    "high_score INTEGER",
    "low_score INTEGER",
    "last_3_avg REAL",
    "last_5_avg REAL",
    "selections INTEGER",
    "sel_c REAL", "sel_vc REAL", "sel_bc REAL", "sel_emg REAL",
    "owned_by REAL",
    "adp INTEGER",
    "proj_avg REAL",
    "tog INTEGER",
    "career_avg REAL",
]

player_fields += [f"vs_r{r} REAL" for r in vs_rounds]
player_fields += ["leagues_rostered REAL", "last_3_proj_avg REAL"]

# Create player_raw table
cur.execute(f"CREATE TABLE player_raw ({', '.join(player_fields)})")

# Insert player rows
for p in players:
    s = p.get("stats", {})
    pos = p.get("positions", [])
    t = s.get("transfers", {})
    vs = s.get("career_avg_vs", {})

    row = [
        p.get("id"),
        f"{p.get('first_name')} {p.get('last_name')}",
        p.get("slug"),
        p.get("dob"),
        p.get("squad_id"),
        p.get("cost"),
        p.get("status"),
        pos[0] if len(pos) > 0 else None,
        pos[1] if len(pos) > 1 else None,
        p.get("is_bye"),
        p.get("locked"),
    ]

    row += [s.get("prices", {}).get(r) for r in price_rounds]
    row += [s.get("scores", {}).get(r) for r in score_rounds]
    row += [s.get("ranks", {}).get(r) for r in rank_rounds]

    for r in transfer_rounds:
        row.append(t.get(r, {}).get("in"))
        row.append(t.get(r, {}).get("out"))

    row += [
        s.get("season_rank"),
        s.get("games_played"),
        s.get("total_points"),
        s.get("avg_points"),
        s.get("high_score"),
        s.get("low_score"),
        s.get("last_3_avg"),
        s.get("last_5_avg"),
        s.get("selections"),
        s.get("selections_info", {}).get("c"),
        s.get("selections_info", {}).get("vc"),
        s.get("selections_info", {}).get("bc"),
        s.get("selections_info", {}).get("emg"),
        s.get("owned_by"),
        s.get("adp"),
        s.get("proj_avg"),
        s.get("tog"),
        s.get("career_avg"),
    ]

    row += [vs.get(r) for r in vs_rounds]
    row += [s.get("leagues_rostered"), s.get("last_3_proj_avg")]

    cur.execute(f"INSERT INTO player_raw VALUES ({','.join(['?'] * len(row))})", row)

# --- Build coach_raw CREATE TABLE ---
coach_fields = ["id INTEGER PRIMARY KEY"]
coach_fields += [f"venue_r{r} REAL" for r in ["6", "190", "40"]]  # sample key venues
coach_fields += [f"opp_r{r} REAL" for r in ["80", "50", "120"]]   # sample key opponents

coach_fields += [f"proj_score_r{r} INTEGER" for r in proj_score_rounds]
coach_fields += [f"proj_price_r{r} INTEGER" for r in proj_price_rounds]
coach_fields += [f"break_even_r{r} INTEGER" for r in be_rounds]
coach_fields += [f"be_pct_r{r} INTEGER" for r in be_pct_rounds]

coach_fields += [
    "last_3_proj_avg REAL",
    "last_3_tog_avg REAL",
    "consistency INTEGER",
    "in_20_avg INTEGER",
    "out_20_avg INTEGER",
    "draft_selections INTEGER",
    "sel_c REAL", "sel_vc REAL", "sel_bc REAL", "sel_emg REAL",
    "proj_score INTEGER",
    "break_even INTEGER",
    "last_5_tog_avg REAL"
]

for r in coach_transfer_rounds:
    coach_fields.append(f"trans_r{r}_in INTEGER")
    coach_fields.append(f"trans_r{r}_out INTEGER")

# Create coach_raw table
cur.execute(f"CREATE TABLE coach_raw ({', '.join(coach_fields)})")

# Insert coach rows
for cid, c in coaches.items():
    row = [int(cid)]

    row += [c.get("venues", {}).get(r) for r in ["6", "190", "40"]]
    row += [c.get("opponents", {}).get(r) for r in ["80", "50", "120"]]
    row += [c.get("proj_scores", {}).get(r) for r in proj_score_rounds]
    row += [c.get("proj_prices", {}).get(r) for r in proj_price_rounds]
    row += [c.get("break_evens", {}).get(r) for r in be_rounds]
    row += [c.get("be_pct", {}).get(r) for r in be_pct_rounds]

    row += [
        c.get("last_3_proj_avg"),
        c.get("last_3_tog_avg"),
        c.get("consistency"),
        c.get("in_20_avg"),
        c.get("out_20_avg"),
        c.get("draft_selections"),
        c.get("draft_selections_info", {}).get("c"),
        c.get("draft_selections_info", {}).get("vc"),
        c.get("draft_selections_info", {}).get("bc"),
        c.get("draft_selections_info", {}).get("emg"),
        c.get("proj_score"),
        c.get("break_even"),
        c.get("last_5_tog_avg")
    ]

    for r in coach_transfer_rounds:
        row.append(c.get("transfers", {}).get(r, {}).get("in"))
        row.append(c.get("transfers", {}).get(r, {}).get("out"))

    cur.execute(f"INSERT INTO coach_raw VALUES ({','.join(['?'] * len(row))})", row)

# --- Join into player_coach_combined
cur.execute("CREATE TABLE player_coach_combined AS SELECT * FROM player_raw LEFT JOIN coach_raw USING(id)")

conn.commit()
conn.close()
print("✅ All tables created with dynamic rounds and full reset.")
