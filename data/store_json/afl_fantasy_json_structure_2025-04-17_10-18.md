
# AFL Fantasy JSON Structure Reference

This document outlines the data structures and field types found in each of the core AFL Fantasy JSON files.

---

## `players.json`
**Structure:** List of player objects

**Each player object includes:**
- `id` (int)
- `first_name` / `last_name` / `slug` (str)
- `dob` (YYYY-MM-DD)
- `squad_id` (int)
- `positions` (List[int])
- `status` / `locked` / `is_bye` (bool/int)
- `stats` (dict)
  - `prices`, `scores`, `ranks` – dict of {round_number: value}
  - `season_rank`, `avg_points`, `games_played`, `last_3_avg`, `proj_avg` (float/int)
  - `career_avg_vs` – dict of {squad_id: float}
  - `selections_info` – dict of selection % for C, VC, EMG
- `tog` (Time on ground) (float)
- `owned_by`, `adp`, `proj_avg`, `career_avg`, etc.

---

## `coach_players.json`
**Structure:** Dict of `player_id` → metadata

**Each player object includes:**
- `proj_scores` (dict of round_id: float)
- `proj_prices` / `break_evens` / `be_pct` (dicts)
- `proj_score`, `break_even`, `last_3_proj_avg` (float)
- `last_3_tog_avg`, `last_5_tog_avg`, `consistency` (float)
- `in_20_avg`, `out_20_avg` (float)
- `transfers` – dict of round → {`in`, `out`} (int)
- `venues` / `opponents` – dict of ID → avg_score (float)
- `draft_selections_info` – dict of selection roles and %s

---

## `players_venue_stats.json` / `players_opp_stats.json`
**Structure:** Dict of `player_id` → Dict of `venue_id` or `opponent_id` → Stat object

**Each stat object includes:**
- `GP`, `TOG`, `score` (float)
- Standard AFL metrics:
  - `K`, `H`, `D`, `ED`, `IED`, `T`, `FF`, `FA`, `HO`, `G`, `B`
  - Advanced: `CP`, `UCP`, `CL`, `SP`, `GA`, `CS`, `CM`, `FD`, `I50`, `R50`

---

## `rounds.json`
**Structure:** List of round objects

**Each round object includes:**
- `id` (int)
- `start`, `end`, `lifted_at` (timestamp strings)
- `status` (str: "complete", "in_progress", etc.)
- `bye_squads` / `locked` (List[int])
- `is_bye`, `is_partial_bye`, `is_final` (int/bool)
- `matches`: list of match objects:
  - `home_squad_id`, `away_squad_id`, `venue_id`, `status`, `date`, `score`, etc.

---

## `show_my.json`
**Structure:** Dict with `result` field

**`result` fields include:**
- `name`, `user_id`, `id` (str/int)
- `value`, `salary_cap`, `points` (int)
- `lineup` (dict)
  - `"1"`, `"2"`, `"3"`, `"4"`: Lists of player_ids (on-field)
  - `bench`: Dict with positional lists and `emergency` list
  - `captain`, `vice_captain` (player_ids)
- `formation` (str)
- `scoreflow` (dict of round_id: points)

---

## `snapshot.json`
**Structure:** Dict with `result` field

**`result` fields include:**
- `name`, `firstname`, `lastname`, `id`, `points` (str/int)
- `round_rank`, `rank`, `num_teams` (int)
- `scoreflow`, `league_scoreflow` – dict of round_id: points
- `rank_history`, `round_rank_history` – dict of round_id: rank

---

## `squads.json`
**Structure:** List of team dicts

Each team object:
- `id` (int)
- `name`, `short_name`, `full_name` (str)

---

## `venues.json`
**Structure:** List of venue dicts

Each venue object:
- `id` (int)
- `name`, `short_name` (str)
- `timezone` (str)

---

This reference can be used to write database schemas, normalize the JSON data, or flatten nested structures for analytics and ML pipelines.
