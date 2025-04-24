import json
import csv
import pandas as pd

# Load coach player transfers
with open("coach_players.json", "r") as f:
    coach_data = json.load(f)

# Load player names
with open("players.json", "r") as f:
    players_data = json.load(f)
id_to_name = {str(player["id"]): f"{player['first_name']} {player['last_name']}" for player in players_data}
id_to_status = {str(player["id"]): player["status"] for player in players_data}
id_to_cost = {str(player["id"]): player["cost"] for player in players_data}
id_to_avg_points = {
    str(player["id"]): player.get("stats", {}).get("avg_points", None) for player in players_data
}
id_to_proj_avg = {
    str(player["id"]): player.get("stats", {}).get("proj_avg", None) for player in players_data
}
id_to_owned_by = {
    str(player["id"]): player.get("stats", {}).get("owned_by", None) for player in players_data
}

# Find all rounds
all_rounds = set()
for player_data in coach_data.values():
    if "transfers" in player_data:
        all_rounds.update(player_data["transfers"].keys())
all_rounds = sorted(int(r) for r in all_rounds)

# Collect total ins/outs per round for normalization
total_transfers_per_round = {r: {"in": 0, "out": 0} for r in all_rounds}
for player_data in coach_data.values():
    transfers = player_data.get("transfers", {})
    for r, d in transfers.items():
        r = int(r)
        total_transfers_per_round[r]["in"] += d.get("in", 0)
        total_transfers_per_round[r]["out"] += d.get("out", 0)

# Build long-form dataset
records = []
for pid, pdata in coach_data.items():
    name = id_to_name.get(pid, f"Unknown_{pid}")
    status = id_to_status.get(pid, "unknown")
    cost = id_to_cost.get(pid)
    avg_points = id_to_avg_points.get(pid)
    proj_avg = id_to_proj_avg.get(pid)
    owned_by = id_to_owned_by.get(pid)
    transfers = pdata.get("transfers", {})
    
    for rnd in all_rounds:
        rstr = str(rnd)
        t_in = transfers.get(rstr, {}).get("in", 0)
        t_out = transfers.get(rstr, {}).get("out", 0)
        net = t_in - t_out
        t_in_pct = t_in / total_transfers_per_round[rnd]["in"] * 100 if total_transfers_per_round[rnd]["in"] else 0
        t_out_pct = t_out / total_transfers_per_round[rnd]["out"] * 100 if total_transfers_per_round[rnd]["out"] else 0
        tag = "hot_pick" if t_in > 2000 else "falling" if net < -500 else ""

        records.append({
            "player_name": name,
            "round": rnd,
            "transfers_in": t_in,
            "transfers_out": t_out,
            "net_transfers": net,
            "transfer_in_pct": round(t_in_pct, 2),
            "transfer_out_pct": round(t_out_pct, 2),
            "tag": tag,
            "status": status,
            "cost": cost,
            "avg_points": avg_points,
            "proj_avg": proj_avg,
            "owned_by_pct": owned_by
        })

df_long = pd.DataFrame(records)

# Save enhanced long-form CSV
enhanced_csv_path = "player_transfer_enhanced_longform.csv"
df_long.to_csv(enhanced_csv_path, index=False)