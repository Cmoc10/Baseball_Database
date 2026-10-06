# Baseball League Management

A MySQL database for a baseball league (teams, players, managers, and season stats) plus a Python/Tkinter desktop app for searching and managing that data.

## Files

| File | Description |
|------|-------------|
| `baseball_league.sql` | Schema, seed data, views, indexes, CSV loading, and sample queries |
| `baseball_app.py` | Tkinter GUI that connects to the database via `mysql-connector-python` |

> Rename the files above to match whatever you saved them as.

## Requirements

- MySQL Server 8.0+
- Python 3.8+
- `mysql-connector-python`
- Tkinter (bundled with most Python installs; on Debian/Ubuntu: `sudo apt install python3-tk`)

```bash
pip install mysql-connector-python
```

## Database

### Schema

| Table | Purpose |
|-------|---------|
| `league` | Leagues and divisions (AL/NL, East/Central/West) |
| `team` | Teams, city, stadium, salary total; references `league` |
| `manager` | Managers, hire date, salary; references `team` |
| `place` | Player positions (named `place` because `position` is a reserved word) |
| `player` | Player bio, contract, handedness, size, birthplace; references `team` and `place` |
| `player_stats` | Per-season batting and pitching stats; references `player` (cascade delete) |

Foreign keys to `team`, `league`, and `place` use `ON DELETE RESTRICT`.

### Seed data

The script inserts 6 league/division rows and 10 positions (P, C, 1B, 2B, 3B, SS, LF, CF, RF, DH). Teams, players, and stats are loaded from CSV files.

### Views

- `active_players`: players where `is_active = TRUE`
- `batting_leaders`: batting avg, HR, RBI, OPS (min. 400 at-bats), sorted by average
- `pitching_leaders`: wins, ERA, saves, WHIP (min. 50 innings), sorted by ERA
- `team_payroll`: roster size, total/average/highest salary per team (active players)

### Indexes

Indexes on player team, position, and name; stats year and player; batting average; and ERA.

### Setup

1. Create the database (the script runs `USE baseball_league;` but does not create it):

   ```sql
   CREATE DATABASE baseball_league;
   ```

2. Create an application user (matches the defaults in the app):

   ```sql
   CREATE USER 'baseball_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON baseball_league.* TO 'baseball_user'@'localhost';
   ```

3. Prepare three CSV files, each with a header row (skipped on load), with columns in the same order as the matching table:
   - `baseball_teams.csv` → `team`
   - `baseball_players.csv` → `player`
   - `baseball_stats.csv` → `player_stats`

4. Find where MySQL allows file imports:

   ```sql
   SHOW VARIABLES LIKE 'secure_file_priv';
   ```

   Put the CSVs in that folder and update the `LOAD DATA INFILE` paths in the script. Use full paths with forward slashes (e.g. `C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/baseball_teams.csv`). Backslashes are treated as escape characters in MySQL strings.

5. Run the script:

   ```bash
   mysql -u root -p < baseball_league.sql
   ```

The script loads each CSV into a temporary table, copies it into the real table, then drops the temporary tables.

### Sample queries (included at the end of the script)

- Top batting averages for 2023
- Top ERA for 2023
- Team payroll rankings
- Average batting stats by position (non-pitchers)

## Desktop app

### Configuration

Edit the connection settings in `BaseballLeagueApp.__init__`:

```python
self.db_config = {
    'host': 'localhost',
    'user': 'baseball_user',
    'password': 'your_password',
    'database': 'baseball_league'
}
```

### Run

```bash
python baseball_app.py
```

### Tabs and features

| Tab | What it does |
|-----|--------------|
| **Player Search** | Search players by full or partial name; shows team, position, salary, jersey number, active status |
| **Team Search** | Search teams by full or partial name; shows city, league, division, founded year, total salary |
| **Player Management** | Add a player; update salary; retire a player (sets inactive and salary to 0); delete a player (and their stats); trade a player to a new team; swap teams between two players |
| **Stat Management** | Update games played, runs, and hits for a player's existing season row |
| **Manager Management** | Hire a manager (name, birth date, hire date, salary, team); fire a manager |

All queries are parameterized, and each action opens its own short-lived database connection.

## Known issues and limitations

These are worth fixing before relying on the project:

**SQL script**
- **No auto-increment IDs.** `player_id`, `manager_id`, and `stat_id` are plain `INT` primary keys. The app inserts players and managers without an ID, so those inserts will fail. Add `AUTO_INCREMENT` to those columns (and `team_id` if you add teams from the app).
- **ERA sample query fails.** It selects `strikeouts`, which isn't a column in the `pitching_leaders` view. Add `s.pitching_strikeouts` to the view and select that instead.
- **`team_payroll` hides empty teams.** `WHERE p.is_active = TRUE` turns the `LEFT JOIN` into an inner join, so teams with no active players disappear. Move that condition into the `ON` clause.
- **No manager data is loaded.** There is no CSV or insert for `manager`.

**Python app**
- **Duplicate "Trade Players" section.** `create_player_management_tab` builds two frames with the same title; the first (single-player trade) and second (two-player swap) both render but share a label.
- **Two-player swap may not work.** The `UPDATE ... SET p1.team_id = p2.team_id, p2.team_id = p1.team_id` pattern can leave both players on the same team in MySQL. Fetch both team IDs first and run two separate updates in one transaction.
- **Name-based lookups.** Updates, retirements, deletes, and trades match on `player_name`, so duplicate names affect every matching row.
- **Retiring zeroes the salary**, which permanently loses the previous value.
- **New players get placeholder values** (`bats='R'`, `throws='R'`, `jersey_number=99`).
- **Stat updates only edit existing rows.** If the player has no row for that season, nothing is inserted and the app still reports success.
- **Search joins exclude incomplete rows.** Players without a team or position won't appear in Player Search.
- **Hard-coded credentials.** Move the password to an environment variable or config file that isn't committed to version control.
- **Connection cleanup in `delete_player`.** `connection.close()` is outdented outside the `finally` block; indent it under `finally`.
- **Dropdowns load once at startup.** Newly added teams won't appear until the app is restarted.

## License

Add a license of your choice here.
