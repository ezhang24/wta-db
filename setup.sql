-- Table definitions for WTA database.
DROP TABLE IF EXISTS tournament_history;
DROP TABLE IF EXISTS match_result;
DROP TABLE IF EXISTS tournament;
DROP TABLE IF EXISTS ranking;
DROP TABLE IF EXISTS player;

-- Defines a WTA player including all player information.
CREATE TABLE player (
    -- Provided in the original dataset
    player_id       CHAR(6),
    -- Player name
    first_name     VARCHAR(20) NOT NULL,
    last_name      VARCHAR(20) NOT NULL,
    -- Dominant hand
    hand            CHAR(1) NOT NULL,
    -- Date of birth
    dob             DATE NOT NULL,
    -- Nationality represented by 3 letter country code
    country         CHAR(3) NOT NULL,
    -- Height is represented in centimeters
    height          INT NOT NULL,
    -- Player must be either right-handed or left-handed
    CHECK (hand IN ('R', 'L')),
    PRIMARY KEY (player_id)
);

-- Defines the current WTA rankings table including associated player
-- and number of player points.
CREATE TABLE ranking (
    player_id               CHAR(6),
    `rank`                  INT,
    -- Number of player points earned from tournaments
    player_points           INT NOT NULL,
    -- Number of tournaments played in the calendar year
    tournaments_played      INT NOT NULL,
    PRIMARY KEY (player_id, `rank`),
    -- Automatically update a player ID and country if changed or delete
    -- from table when necessary
    FOREIGN KEY (player_id) REFERENCES player(player_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Defines a tournament table including where the tournament is played and
-- the level.
CREATE TABLE tournament (
    -- Provided in the original dataset
    tournament_id           VARCHAR(4),
    tournament_name         VARCHAR(25) NOT NULL,
    -- Playing surface
    surface                 VARCHAR(10) NOT NULL,
    -- Draw size contains the maximum number of players that can be
    -- entered in the tournament
    draw_size               INT NOT NULL,
    -- Tournament level defined as labels in the dataset
    -- (e.g. G represents Grand Slam)
    tournament_level        CHAR(1) NOT NULL,
    -- The playing surface must be either clay, hard, or grass
    CHECK (surface IN ('Clay', 'Hard', 'Grass')),
    PRIMARY KEY (tournament_id)
);

-- Defines a match result between two WTA players including match
-- statistics.
CREATE TABLE match_result (
    match_id            INT AUTO_INCREMENT,
    tournament_id       VARCHAR(4) NOT NULL,
    -- Start date of the tournament
    tournament_date          DATE NOT NULL,
    -- Score is formatted with hyphens (e.g. 6-2, 6-4)
    score               VARCHAR(20) NOT NULL,
    -- Duration of the match
    minutes             INT NOT NULL,
    winner_id           CHAR(6) NOT NULL,
    -- Winner statistics including number of aces, break points saved,
    -- serve percentage, and double faults
    winner_aces         INT,
    winner_bp_saved     INT,
    winner_dfs          INT,
    loser_id            CHAR(6) NOT NULL,
    -- Loser statistics including number of aces, break points saved,
    -- serve percentage, and double faults
    loser_aces          INT,
    loser_bp_saved      INT,
    loser_dfs           INT,
    PRIMARY KEY (match_id),
    -- Automatically update or delete winner ID or loser ID when changes
    -- are made
    FOREIGN KEY (winner_id) REFERENCES player(player_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (loser_id) REFERENCES player(player_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    -- Automatically update or delete tournament ID when tournament changes
    -- are made
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Defines a history of past winners and finalists from different tournaments
-- on the WTA tour.
CREATE TABLE tournament_history (
    tournament_id       VARCHAR(25) NOT NULL,
    tournament_year     CHAR(4) NOT NULL,
    winner_id           CHAR(6),
    finalist_id         CHAR(6) NOT NULL,
    match_id            INT NOT NULL,
    PRIMARY KEY (tournament_id, tournament_year),
    -- Automatically update player IDs when changed or deleted
    FOREIGN KEY (winner_id) REFERENCES player(player_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (finalist_id) REFERENCES player(player_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    -- Automatically update match IDs when changed or deleted
    FOREIGN KEY (match_id) REFERENCES match_result(match_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
    -- Automatically update tournament IDs and year when changed or deleted
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

-- Creates index on the match_result table to improve performance time
-- of related queries.
CREATE INDEX idx_min ON match_result (minutes);
