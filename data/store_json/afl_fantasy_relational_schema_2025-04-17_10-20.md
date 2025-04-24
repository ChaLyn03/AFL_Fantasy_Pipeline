
# AFL Fantasy Relational Schema (ERD Style)

This schema defines the relational model to represent all AFL Fantasy JSON data in structured tables. Foreign keys, relationships, and normalized entities are defined to support database integration.

---

## Table: `players`
- `player_id` (PK)
- `first_name`, `last_name`, `slug`
- `dob`
- `squad_id` (FK → squads.squad_id)
- `positions` (List[int])
- `status`, `locked`, `is_bye`
- `career_avg`, `proj_avg`, `tog`, `owned_by`, `adp`
- `selections`, `selections_info` (json)
- `career_avg_vs` (json)

---

## Table: `player_stats`
- `player_id` (FK → players.player_id)
- `round` (PK)
- `price`, `score`, `rank`
- `season_rank`, `games_played`, `avg_points`, `high_score`, `low_score`
- `last_3_avg`, `last_5_avg`, `last_3_proj_avg`, `last_3_tog_avg`, `last_5_tog_avg`

---

## Table: `coach_projections`
- `player_id` (FK → players.player_id)
- `round` (PK)
- `proj_score`, `proj_price`, `break_even`, `be_pct`
- `consistency`, `in_20_avg`, `out_20_avg`
- `transfers_in`, `transfers_out`

---

## Table: `player_venue_stats`
- `player_id` (FK → players.player_id)
- `venue_id` (FK → venues.venue_id)
- `GP`, `TOG`, `score`, `K`, `H`, `D`, `ED`, `IED`, `T`, `FF`, `FA`, `HO`, `G`, `B`
- `CP`, `UCP`, `CL`, `SP`, `GA`, `CS`, `CM`, `FD`, `I50`, `R50`

---

## Table: `player_opp_stats`
- `player_id` (FK → players.player_id)
- `opponent_squad_id` (FK → squads.squad_id)
- (Same stat fields as above)

---

## Table: `rounds`
- `round_id` (PK)
- `start`, `end`, `status`, `lifted_at`
- `is_bye`, `is_partial_bye`, `is_final`
- `lockout`, `saturday_lockout`

---

## Table: `matches`
- `match_id` (PK)
- `round_id` (FK → rounds.round_id)
- `home_squad_id`, `away_squad_id` (FK → squads.squad_id)
- `venue_id` (FK → venues.venue_id)
- `status`, `date`, `home_score`, `away_score`, `goals`, `behinds`

---

## Table: `squads`
- `squad_id` (PK)
- `name`, `short_name`, `full_name`

---

## Table: `venues`
- `venue_id` (PK)
- `name`, `short_name`, `timezone`

---

## Table: `user_team`
- `user_id` (PK)
- `name`, `team_id`, `salary_cap`, `value`
- `points`, `scoreflow` (json)
- `formation`
- `season_trades_left`, `week_trades_left`
- `start_round`, `activated_at`

---

## Table: `user_team_lineup`
- `user_id` (FK → user_team.user_id)
- `round` (PK)
- `position_group` (int: 1=DEF, 2=MID, etc.)
- `player_id` (FK → players.player_id)
- `role`: 'field', 'bench', 'emergency', 'captain', 'vice_captain'

---

## Table: `user_snapshot`
- `user_id` (FK → user_team.user_id)
- `round` (PK)
- `points`, `round_rank`, `rank`
- `rank_history`, `round_rank_history`, `league_scoreflow` (json)

---

This schema supports comprehensive tracking, modeling, and optimization of fantasy teams and real-world match contexts.
