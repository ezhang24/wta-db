-- Setup code for defining procedural SQL in the WTA database.
DROP FUNCTION IF EXISTS find_matchup_history;
DROP FUNCTION IF EXISTS find_highest_ranked_player;
DROP PROCEDURE IF EXISTS input_match_results;
DROP PROCEDURE IF EXISTS update_tournaments_played;
DROP TRIGGER IF EXISTS trg_match_result_insert;

-- A function that executes given two player names. Reports their
-- most recent score results with the winner name.
-- Returns NULL if no matches were played between them or player
-- is not in the database.
DELIMITER !

CREATE FUNCTION find_matchup_history(
    player1_first_name VARCHAR(20),
    player1_last_name VARCHAR(20),
    player2_first_name VARCHAR(20),
    player2_last_name VARCHAR(20)
) RETURNS VARCHAR(30) DETERMINISTIC BEGIN

    DECLARE player1_id CHAR(6) DEFAULT NULL;
    DECLARE player2_id CHAR(6) DEFAULT NULL;
    DECLARE match_score VARCHAR(20) DEFAULT NULL;
    DECLARE winner_name VARCHAR(40) DEFAULT NULL;
    DECLARE w_id CHAR(6) DEFAULT NULL;

    SET player1_id = (
            SELECT player_id
            FROM player
            WHERE first_name = player1_first_name
                AND last_name = player1_last_name
        );
    SET player2_id = (
            SELECT player_id
            FROM player
            WHERE first_name = player2_first_name
                AND last_name = player2_last_name
        );

    -- Returns null if either player is not in the database
    IF player1_id IS NULL OR player2_id IS NULL
        THEN RETURN NULL;
    END IF;

    SELECT score,
        winner_id INTO match_score,
        w_id
    FROM match_result
    WHERE (
            winner_id = player1_id
            AND loser_id = player2_id
        )
        OR (
            winner_id = player2_id
            AND loser_id = player1_id
        )
    ORDER BY tournament_date DESC
    LIMIT 1;

    -- No match was played between the two specified players
    IF match_score IS NULL
        THEN RETURN NULL;
    END IF;

    IF w_id = player1_id
        THEN SET winner_name = (CONCAT(player1_first_name, ' ', player1_last_name));
    ELSE
        SET winner_name = (CONCAT(player2_first_name, ' ', player2_last_name));
    END IF;

    RETURN CONCAT(winner_name, ' ', match_score);

END !
DELIMITER ;

-- A procedure to execute when given a match result data. If the match is
-- a final, update the tournament history table accordingly. Update
-- the match result table as well.
DELIMITER !
CREATE PROCEDURE input_match_results(
    is_final TINYINT,
    tournament_id VARCHAR(4),
    match_date DATE,
    score VARCHAR(20),
    minutes INT,
    winner_id CHAR(6),
    winner_aces INT,
    winner_bp_saved INT,
    winner_dfs INT,
    loser_id CHAR(6),
    loser_aces INT,
    loser_bp_saved INT,
    loser_dfs INT
) BEGIN

    DECLARE new_match_id INT DEFAULT NULL;
    DECLARE match_year CHAR(4) DEFAULT NULL;

    SET new_match_id = ((SELECT MAX(match_id) FROM match_result) + 1);
    SET match_year = (SELECT YEAR(match_date));

    INSERT INTO match_result
    VALUES (
            new_match_id,
            tournament_id,
            match_date,
            score,
            minutes,
            winner_id,
            winner_aces,
            winner_bp_saved,
            winner_dfs,
            loser_id,
            loser_aces,
            loser_bp_saved,
            loser_dfs
        );

    IF is_final = 1
        THEN INSERT INTO tournament_history
        VALUES (
                tournament_id,
                match_year,
                winner_id,
                loser_id,
                new_match_id
            );
    END IF;

END !
DELIMITER ;

-- A procedure that is called after inserting data into match results
-- to update the number of tournaments played (if necessary) in the
-- rankings table.
DELIMITER !
CREATE PROCEDURE update_tournaments_played(
    p_id CHAR(6),
    t_id VARCHAR(4),
    m_date DATE
) BEGIN

    DECLARE num_matches INT DEFAULT NULL;
    DECLARE ranked_id CHAR(6) DEFAULT NULL;
    DECLARE curr_played INT DEFAULT NULL;

    SET num_matches = (
            SELECT COUNT(*)
            FROM match_result
            WHERE tournament_id = t_id
                AND tournament_date = m_date
                AND (
                    winner_id = p_id
                    OR loser_id = p_id
                )
        );

    SET ranked_id = (SELECT player_id FROM ranking WHERE player_id = p_id);

    IF ranked_id IS NOT NULL
        THEN SET curr_played = (
                SELECT tournaments_played
                FROM ranking
                WHERE player_id = p_id
            );
        END IF;

    IF num_matches = 1 AND ranked_id IS NOT NULL
        THEN
        UPDATE ranking
        SET tournaments_played = curr_played + 1
        WHERE player_id = p_id;
    END IF;

END !
DELIMITER ;

-- A trigger to handle inserts to the match results table. If the inserted
-- match is from a new tournament, update the number of tournaments played for
-- the specified player if they are in the rankings table.
DELIMITER !
CREATE TRIGGER trg_match_result_insert AFTER INSERT
    ON match_result FOR EACH ROW
BEGIN

    CALL update_tournaments_played(
        NEW.winner_id,
        NEW.tournament_id,
        NEW.tournament_date
    );
    CALL update_tournaments_played(
        NEW.loser_id,
        NEW.tournament_id,
        NEW.tournament_date
    );
END !
DELIMITER ;

-- A function that returns the highest ranked player given a specific
-- country. Returns null if no player from that country exists in the
-- top 20. Country is given in the 3 digit character code.
DELIMITER !

CREATE FUNCTION find_highest_ranked_player(
    player_country CHAR(3)
) RETURNS VARCHAR(40) DETERMINISTIC BEGIN

    DECLARE player_first_name VARCHAR(20) DEFAULT NULL;
    DECLARE player_last_name VARCHAR(20) DEFAULT NULL;
    DECLARE player_rank INT DEFAULT NULL;

    SET player_rank = (
            SELECT MIN(`rank`)
            FROM ranking
                NATURAL JOIN player
            WHERE country = player_country
        );

    SELECT first_name,
        last_name INTO player_first_name,
        player_last_name
    FROM ranking
        NATURAL JOIN player
    WHERE `rank` = player_rank;

    RETURN CONCAT(player_first_name, ' ', player_last_name, ' ', player_rank);

END !
DELIMITER ;
