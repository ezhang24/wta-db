-- Provides a set of queries on the WTA database.
-- Reports the past tournament winners first name and last name
-- based on the tournament name ordered by year.
SELECT tournament_year,
    first_name,
    last_name
FROM (
        SELECT tournament_name,
            tournament_year,
            winner_id
        FROM tournament
            NATURAL JOIN tournament_history
        WHERE tournament_name = 'Australian Open'
    ) AS T
    JOIN player ON winner_id = player_id
ORDER BY tournament_year;

-- Search for a list of players outside of the current rankings of the
-- Top 20, ordered by age.
SELECT first_name,
    last_name,
    TIMESTAMPDIFF(YEAR, dob, current_date()) AS age
FROM player
WHERE player_id NOT IN (
        SELECT player_id
        FROM ranking
    )
ORDER BY age;

-- Report the total number of matches played on each surface
-- based on a specified player name.
SELECT surface,
    COUNT(*) AS num_matches
FROM (
        SELECT tournament_id
        FROM match_result
            JOIN (
                SELECT player_id
                FROM player
                WHERE first_name = 'Ons'
                    AND last_name = 'Jabeur'
            ) AS P ON (
                winner_id = player_id
                OR loser_id = player_id
            )
    ) AS M
    NATURAL JOIN tournament
GROUP BY surface;
