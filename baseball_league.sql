-- Create the database
USE baseball_league;

-- Create League table
CREATE TABLE league (
    league_id INT,
    league_name CHAR(50),
    division_name CHAR(30),
    founding_year INT,
    PRIMARY KEY(league_id)
);

-- Create Team table
CREATE TABLE team (
    team_id INT,
    team_name CHAR(50),
    city CHAR(30),
    league_id INT,
    founded_year INT,
    total_salary NUMERIC(12,2),
    stadium_name CHAR(50),
    PRIMARY KEY(team_id),
    FOREIGN KEY(league_id) REFERENCES league(league_id) ON DELETE RESTRICT
);

-- Create Manager table
CREATE TABLE manager (
    manager_id INT,
    manager_name CHAR(50),
    birth_date DATE,
    hire_date DATE,
    salary NUMERIC(10,2),
    team_id INT,
    PRIMARY KEY(manager_id),
    FOREIGN KEY(team_id) REFERENCES team(team_id) ON DELETE RESTRICT
);

-- Create Place table (formerly Position)
CREATE TABLE place (
    position_id INT,
    position_name CHAR(30),
    position_abbrev CHAR(5),
    avg_salary NUMERIC(10,2),
    PRIMARY KEY(position_id)
);

-- Create Player table
CREATE TABLE player (
    player_id INT,
    player_name CHAR(50),
    birth_date DATE,
    salary NUMERIC(10,2),
    team_id INT,
    position_id INT,
    jersey_number INT,
    contract_end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    bats CHAR(1),
    throws CHAR(1),
    height_inches INT,
    weight_lbs INT,
    birth_city CHAR(30),
    birth_state CHAR(2),
    PRIMARY KEY(player_id),
    FOREIGN KEY(team_id) REFERENCES team(team_id) ON DELETE RESTRICT,
    FOREIGN KEY(position_id) REFERENCES place(position_id) ON DELETE RESTRICT
);

-- Create Stats table with baseball-specific statistics
CREATE TABLE player_stats (
    stat_id INT,
    player_id INT,
    season_year INT,
    games_played INT,
    games_started INT,
    at_bats INT,
    runs INT,
    hits INT,
    doubles INT,
    triples INT,
    home_runs INT,
    rbis INT,
    stolen_bases INT,
    caught_stealing INT,
    walks INT,
    strikeouts INT,
    batting_avg DECIMAL(4,3),
    on_base_pct DECIMAL(4,3),
    slugging_pct DECIMAL(4,3),
    ops DECIMAL(4,3),
    -- Pitching stats
    innings_pitched DECIMAL(5,1),
    wins INT,
    losses INT,
    era DECIMAL(4,2),
    games_finished INT,
    complete_games INT,
    shutouts INT,
    saves INT,
    hits_allowed INT,
    earned_runs INT,
    pitching_strikeouts INT,
    pitching_walks INT,
    whip DECIMAL(4,3),
    PRIMARY KEY(stat_id),
    FOREIGN KEY(player_id) REFERENCES player(player_id) ON DELETE CASCADE
);

-- Insert base data
INSERT INTO league(league_id, league_name, division_name, founding_year)
VALUES 
(1, 'American League', 'East', 1901),
(2, 'American League', 'Central', 1901),
(3, 'American League', 'West', 1901),
(4, 'National League', 'East', 1876),
(5, 'National League', 'Central', 1876),
(6, 'National League', 'West', 1876);

-- Insert positions
INSERT INTO place(position_id, position_name, position_abbrev, avg_salary)
VALUES
(1, 'Pitcher', 'P', 4200000.00),
(2, 'Catcher', 'C', 2800000.00),
(3, 'First Baseman', '1B', 3900000.00),
(4, 'Second Baseman', '2B', 3100000.00),
(5, 'Third Baseman', '3B', 3500000.00),
(6, 'Shortstop', 'SS', 3700000.00),
(7, 'Left Fielder', 'LF', 3300000.00),
(8, 'Center Fielder', 'CF', 3400000.00),
(9, 'Right Fielder', 'RF', 3300000.00),
(10, 'Designated Hitter', 'DH', 3800000.00);

-- Create useful views
CREATE VIEW active_players AS
SELECT * FROM player WHERE is_active = TRUE;

CREATE VIEW batting_leaders AS
SELECT 
    p.player_name,
    t.team_name,
    s.season_year,
    s.batting_avg,
    s.home_runs,
    s.rbis,
    s.ops
FROM player p
JOIN team t ON p.team_id = t.team_id
JOIN player_stats s ON p.player_id = s.player_id
WHERE s.at_bats >= 400
ORDER BY s.batting_avg DESC;

CREATE VIEW pitching_leaders AS
SELECT 
    p.player_name,
    t.team_name,
    s.season_year,
    s.wins,
    s.era,
    s.saves,
    s.whip
FROM player p
JOIN team t ON p.team_id = t.team_id
JOIN player_stats s ON p.player_id = s.player_id
WHERE s.innings_pitched >= 50
ORDER BY s.era ASC;

CREATE VIEW team_payroll AS
SELECT 
    t.team_name,
    t.city,
    l.league_name,
    l.division_name,
    COUNT(p.player_id) as roster_size,
    SUM(p.salary) as total_payroll,
    AVG(p.salary) as avg_salary,
    MAX(p.salary) as highest_salary
FROM team t
JOIN league l ON t.league_id = l.league_id
LEFT JOIN player p ON t.team_id = p.team_id
WHERE p.is_active = TRUE
GROUP BY t.team_id;

-- Create indexes
CREATE INDEX idx_player_team ON player(team_id);
CREATE INDEX idx_player_position ON player(position_id);
CREATE INDEX idx_stats_year ON player_stats(season_year);
CREATE INDEX idx_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_name ON player(player_name);
CREATE INDEX idx_batting_avg ON player_stats(batting_avg);
CREATE INDEX idx_era ON player_stats(era);

-- Create temporary tables for CSV loading
CREATE TEMPORARY TABLE temp_teams (
    team_id INT,
    team_name CHAR(50),
    city CHAR(30),
    league_id INT,
    founded_year INT,
    total_salary NUMERIC(12,2),
    stadium_name CHAR(50)
);

CREATE TEMPORARY TABLE temp_players (
    player_id INT,
    player_name CHAR(50),
    birth_date DATE,
    salary NUMERIC(10,2),
    team_id INT,
    position_id INT,
    jersey_number INT,
    contract_end_date DATE,
    is_active BOOLEAN,
    bats CHAR(1),
    throws CHAR(1),
    height_inches INT,
    weight_lbs INT,
    birth_city CHAR(30),
    birth_state CHAR(2)
);

CREATE TEMPORARY TABLE temp_stats (
    stat_id INT,
    player_id INT,
    season_year INT,
    games_played INT,
    games_started INT,
    at_bats INT,
    runs INT,
    hits INT,
    doubles INT,
    triples INT,
    home_runs INT,
    rbis INT,
    stolen_bases INT,
    caught_stealing INT,
    walks INT,
    strikeouts INT,
    batting_avg DECIMAL(4,3),
    on_base_pct DECIMAL(4,3),
    slugging_pct DECIMAL(4,3),
    ops DECIMAL(4,3),
    innings_pitched DECIMAL(5,1),
    wins INT,
    losses INT,
    era DECIMAL(4,2),
    games_finished INT,
    complete_games INT,
    shutouts INT,
    saves INT,
    hits_allowed INT,
    earned_runs INT,
    pitching_strikeouts INT,
    pitching_walks INT,
    whip DECIMAL(4,3)
);

select @@secure_file_priv;
SHOW VARIABLES LIKE "secure_file_priv";

-- Load data from CSV files
LOAD DATA INFILE 'ProgramData\MySQL\MySQL Server 8.0\Uploads\baseball_teams.csv'
INTO TABLE temp_teams
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'baseball_players.csv'
INTO TABLE temp_players
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'baseball_stats.csv'
INTO TABLE temp_stats
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Insert data from temp tables to main tables
INSERT INTO team
SELECT * FROM temp_teams;

INSERT INTO player
SELECT * FROM temp_players;

INSERT INTO player_stats
SELECT * FROM temp_stats;

-- Drop temporary tables
DROP TEMPORARY TABLE IF EXISTS temp_teams;
DROP TEMPORARY TABLE IF EXISTS temp_players;
DROP TEMPORARY TABLE IF EXISTS temp_stats;

-- Sample queries
-- Batting average leaders
SELECT player_name, team_name, batting_avg, home_runs, rbis
FROM batting_leaders
WHERE season_year = 2023
LIMIT 10;

-- ERA leaders
SELECT player_name, team_name, era, wins, strikeouts
FROM pitching_leaders
WHERE season_year = 2023
LIMIT 10;

-- Team salary rankings
SELECT team_name, total_payroll, avg_salary
FROM team_payroll
ORDER BY total_payroll DESC;

-- Player stats by position
SELECT pl.position_name,
       AVG(ps.batting_avg) as avg_batting,
       AVG(ps.home_runs) as avg_hr,
       AVG(ps.rbis) as avg_rbi
FROM player p
JOIN place pl ON p.position_id = pl.position_id
JOIN player_stats ps ON p.player_id = ps.player_id
WHERE ps.season_year = 2023
AND pl.position_name != 'Pitcher'
GROUP BY pl.position_name;