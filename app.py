"""
Student name(s): Emily Zhang, Beatriz Avila-Rimer
Student email(s): elzhang@caltech.edu, bea@caltech.edu
High-level program overview

This program creates an interface for either an admin or user of the WTA
database, allowing admins to change/input data and allowing users to make
certain queries and view the existing data.

"""
import sys  # to print error messages to sys.stderr
import mysql.connector
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode
import datetime

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True


# ----------------------------------------------------------------------
# SQL Utility Functions
# ----------------------------------------------------------------------
def get_conn_for_admin():
    """"
    Returns a connected MySQL connector instance for an admin, if connection
    is successful. If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appadmin',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='adminpw',
          database='wtadb'
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            # A fine catchall client-facing message.
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)

def get_conn_for_user():
    """"
    Returns a connected MySQL connector instance for a user, if connection
    is successful. If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appclient',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='clientpw',
          database='wtadb'
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            # A fine catchall client-facing message.
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)

def exists(table, attribute, value):
    """
    Checks to see if a specific value exists in a given table with a given
    attribute.
    """
    cursor = conn.cursor()
    sql = 'SELECT * FROM %s WHERE %s = \'%s\';' % (table, attribute, value)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            return True
        return False
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when checking if user exists. ')
            return

def valid_date(date):
    """
    Checks to see if an input is in a valid date format.
    """
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
def show_tournament_winners():
    """
    Prompts the user to enter a tournament name in the database,
    then shows a list of past winners in the last 3 years. Results
    are sorted by year in ascending order.
    """

    tournament = input('What tournament would you like to view? ')
    sql = """SELECT tournament_year,
                    first_name,
                    last_name
                FROM (
                        SELECT tournament_name,
                            tournament_year,
                            winner_id
                        FROM tournament
                            NATURAL JOIN tournament_history
                        WHERE tournament_name = '%s'
                    ) AS T
                    JOIN player ON winner_id = player_id
                ORDER BY tournament_year;""" % (tournament, )

    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        # row = cursor.fetchone()
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when searching for tournament winners. ')
            return
    if not rows:
        print('No results found.')
    else:
        print(f'{tournament.title()} winners in the database (oldest first):')
        for row in rows:
            (year, first_name, last_name) = row
            print('  ', f'{year}', f'Winner: {first_name} {last_name}')

def show_players_top_20():
    """
    Prompts the user to view players inside or outside the current top 20
    WTA rankings. Ordered by rank when querying for inside the top 20 and
    ordered by ascending age when querying for outside the top 20.
    """
    ans = input('Would you like to see players inside or outside top 20? ')
    while ans.lower() != 'inside' and ans.lower() != 'outside':
        ans = input('Invalid input. Please try again or press (q) to quit: ')
        if ans == 'q':
            quit_ui()
    is_inside = True
    if ans and ans.lower() == 'inside':
        sql = """SELECT `rank`,
                        first_name,
                        last_name,
                        TIMESTAMPDIFF(YEAR, dob, current_date()) AS age
                    FROM ranking NATURAL JOIN player
                    ORDER BY `rank`;"""
    elif ans.lower() == 'outside':
        is_inside = False
        sql = """SELECT first_name,
                        last_name,
                        TIMESTAMPDIFF(YEAR, dob, current_date()) AS age
                    FROM player
                    WHERE player_id NOT IN (
                            SELECT player_id
                            FROM ranking
                        )
                    ORDER BY age;"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        # row = cursor.fetchone()
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when searching for players.')
            return
    if not rows:
        print('No results found.')
    else:
        if is_inside:
            print('Players in the Top 20 (ordered by rank):')
            for row in rows:
                (rank, first_name, last_name, age) = row
                print('  ', f'Rank #{rank}: {first_name} {last_name}, Age: {age}')
        else:
            print('Players outside the Top 20 (youngest first):')
            for row in rows:
                (first_name, last_name, age) = row
                print('  ', f'{first_name} {last_name}, Age: {age}')

def show_surface_count():
    """
    Prompts the user to enter a player name to view the count breakdown of
    matches played on different surfaces.
    """
    player_name = input('Enter a first and last name of player: ')
    player_name = player_name.split()
    first_name, last_name = player_name[0], player_name[1]
    sql = """SELECT surface,
                COUNT(*) AS num_matches
            FROM (
                    SELECT tournament_id
                    FROM match_result
                        JOIN (
                            SELECT player_id
                            FROM player
                            WHERE first_name = '%s'
                                AND last_name = '%s'
                        ) AS P ON (
                            winner_id = player_id
                            OR loser_id = player_id
                        )
                ) AS M
                NATURAL JOIN tournament
            GROUP BY surface;
    """ % (first_name, last_name, )
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        # row = cursor.fetchone()
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when searching for this player.')
            return
    if not rows:
        print(f'No results found for {first_name.title()} {last_name.title()}.')
    else:
        print(f'Number of matches played by {first_name.title()} {last_name.title()} on each surface:')
        for row in rows:
            (surface, count) = row
            print('  ', f'Surface: {surface}, Matches Played: {count}')

def show_player_country():
    """
    Prompts the user to enter in a specific 3 character country code and
    shows the list of players from the specified country.
    """
    country = input('What country would you like to see players from? Please enter its 3 digit character code: ')
    while not exists('player', 'country', country):
        country = input('Invalid country code. Please try again or press (q) to quit: ')
        if country == 'q':
            quit_ui()
    sql = 'SELECT first_name, last_name, hand, height FROM player WHERE country = \'%s\';' % (country)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        # row = cursor.fetchone()
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when searching for this player.')
            return
    if not rows:
        print(f'No results found for {country.upper()}.')
    else:
        print(f'List of players from {country.upper()}:')
        for row in rows:
            (first_name, last_name, hand, height) = row
            print('  ', f'Player Name: {first_name} {last_name}, Dominant Hand: {hand}, Height: {height}')


def input_match_results():
    """
    Prompts the admin to enter in match result data and
    whether or not match was a final. Calls the procedure to add to the
    tournament history table if necessary.
    """
    ans = input('Was this match a final? ')
    if ans and ans.lower()[0] == 'y':
        is_final = 1
    else:
        is_final = 0
    id = input('Input tournament ID: ')
    while not exists('tournament', 'tournament_id', id):
        id = input('Invalid tournament ID. Please try again or press (q) to quit: ')
        if id == 'q':
            quit_ui()
    date = input('Input tournament start date (YYYY-MM-DD): ')
    while not valid_date(date):
        date = input('Invalid date format. Please try again or press (q) to quit: ')
        if date == 'q':
            quit_ui()
    score = input('Input match score (e.g. 6-4, 7-6(3)) or WALKOVER): ')
    while score.isdecimal():
        score = input('Invalid match score. Please try again or press (q) to quit: ')
        if score == 'q':
            quit_ui()
    mins = input('Input the duration of the match in minutes: ')
    while not mins.isdecimal():
        mins = input('Invalid duration. Please try again or press (q) to quit: ')
        if mins == 'q':
            quit_ui()
    winner_id = input('Input the winning player ID: ')
    while not exists('player', 'player_id', winner_id):
        winner_id = input('Invalid winner ID. Please try again or press (q) to quit: ')
        if winner_id == 'q':
            quit_ui()
    loser_id = input('Input losing player ID: ')
    while not exists('player', 'player_id', loser_id):
        loser_id = input('Invalid loser ID. Please try again or press (q) to quit: ')
        if loser_id == 'q':
            quit_ui()
    ans = input('Was this match played? ')
    if ans and ans.lower()[0] == 'y':
        winner_aces = input('Input number of aces by the winner: ')
        while not winner_aces.isdecimal():
            winner_aces = input('Invalid number of aces. Please try again or press (q) to quit: ')
            if winner_aces == 'q':
                quit_ui()
        winner_bp_saved = input('Input number of break points saved by the winner: ')
        while not winner_bp_saved.isdecimal():
            winner_bp_saved = input('Invalid number of break points. Please try again or press (q) to quit: ')
            if winner_bp_saved == 'q':
                quit_ui()
        winner_dfs = input('Input number of double faults by the winner: ')
        while not winner_dfs.isdecimal():
            winner_dfs = input('Invalid number of double faults. Please try again or press (q) to quit: ')
            if winner_dfs == 'q':
                quit_ui()
        loser_aces = input('Input number of aces by the loser: ')
        while not loser_aces.isdecimal():
            loser_aces = input('Invalid number of aces. Please try again or press (q) to quit: ')
            if loser_aces == 'q':
                quit_ui()
        loser_bp_saved = input('Input number of break points saved by the loser: ')
        while not loser_bp_saved.isdecimal():
            loser_bp_saved = input('Invalid number of break points. Please try again or press (q) to quit: ')
            if loser_bp_saved == 'q':
                quit_ui()
        loser_dfs = input('Input number of double faults by the loser: ')
        while not loser_dfs.isdecimal():
            loser_dfs = input('Invalid number of double faults. Please try again or press (q) to quit: ')
            if loser_dfs == 'q':
                quit_ui()
    else:
        winner_aces = 'NULL'
        winner_bp_saved = 'NULL'
        winner_dfs = 'NULL'
        loser_aces = 'NULL'
        loser_bp_saved = 'NULL'
        loser_dfs = 'NULL'
    try:
        sql = """CALL input_match_results('%d', '%s', '%s', '%s', '%s', '%s',
                                        %s, %s, %s, '%s', %s, %s, %s)
            """ % (is_final, id, date, score, mins, winner_id, winner_aces,
                    winner_bp_saved, winner_dfs, loser_id, loser_aces, loser_bp_saved, loser_dfs, )
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        # row = cursor.fetchone()
        # rows = cursor.fetchall()
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when inputting the match data.')
            return
    print('Match results input successfully entered into database. ')

def update_player_information():
    """
    Prompts the admin to enter in new information to update the
    player table.
    """
    print('Who would you like to update? ')
    id = input('Enter a valid ID: ')
    while not exists('player', 'player_id', id):
        id = input('Invalid player ID. Please try again or press (q) to quit: ')
        if id == 'q':
            quit_ui()
    print('What information would you like to update? ')
    print('Select one of the following options: ')
    print('  (f) -- first name')
    print('  (l) -- last name')
    print('  (h) -- hand')
    print('  (d) -- date of birth')
    print('  (c) -- country')
    print('  (g) -- height')
    ans = input('Enter an option: ').lower()
    if ans == 'f':
        name = input('Enter new name: ')
        sql = 'UPDATE player SET first_name = \'%s\' WHERE player_id = \'%s\';' % (name, id)
    elif ans == 'l':
        name = input('Enter new name: ')
        sql = 'UPDATE player SET last_name = \'%s\' WHERE player_id = \'%s\';' % (name, id)
    elif ans == 'h':
        hand = input('Enter new hand: ')
        while hand.lower() != 'r' and hand.lower() != 'l':
            hand = input('Invalid input. Please try again or press (q) to quit: ')
            if hand == 'q':
                quit_ui()
        sql = 'UPDATE player SET hand = \'%s\' WHERE player_id = \'%s\';' % (hand.upper(), id)
    elif ans == 'd':
        dob = input('Enter new dob: ')
        while not valid_date(dob):
            dob = input('Invalid input. Please try again or press (q) to quit: ')
            if dob == 'q':
                quit_ui()
        sql = 'UPDATE player SET dob = \'%s\' WHERE player_id = \'%s\';' % (dob, id)
    elif ans == 'c':
        country = input('Enter new country: ')
        while len(country) != 3 or country.isdecimal():
            country = input('Invalid input. Please try again or press (q) to quit: ')
            if country == 'q':
                quit_ui()
        sql = 'UPDATE player SET country = \'%s\' WHERE player_id = \'%s\';' % (country.upper(), id)
    elif ans == 'g':
        height = input('Enter new height: ')
        while not height.isdecimal():
            height = input('Invalid input. Please try again or press (q) to quit: ')
            if height == 'q':
                quit_ui()
        sql = 'UPDATE player SET height = \'%s\' WHERE player_id = \'%s\';' % (height, id)
    else:
        print('Unknown option.')
        return
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print('Changed player information successfully.')
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when inputting the player data.')
            return

def update_rankings():
    """
    Prompts the admin to enter in the corresponding information to
    change the current Top 20 WTA rankings.
    """
    rank = input('Which rank (1-20) would you like to change? ')
    while not rank.isdecimal() or not (int(rank) >= 1) or not (int(rank) <= 20):
        rank = input('Invalid rank. Please try again or press (q) to quit: ')
        if rank == 'q':
            quit_ui()
    id = input(f'Input new player ID for Rank #{rank}: ')
    while not exists('player', 'player_id', id):
        id = input('Invalid ID. Please try again or press (q) to quit: ')
        if id == 'q':
            quit_ui()
    pts = input(f'Input number of points for Player {id}: ')
    while not pts.isdecimal():
        pts = input('Invalid number. Please try again or press (q) to quit: ')
        if pts == 'q':
            quit_ui()
    t = input(f'Input the number of tournaments played in the calendar year for Player {id}: ')
    while not t.isdecimal():
        t = input('Invalid number. Please try again or press (q) to quit: ')
        if t == 'q':
            quit_ui()
    sql = """UPDATE ranking SET player_id = \'%s\',
                                player_points = %s,
                                tournaments_played = %s
                            WHERE `rank` = %s;""" % (id, pts, t, rank)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print('Updated player ranking successfully.')
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred when inputting the ranking data.')
            return

# ----------------------------------------------------------------------
# Functions for Logging Users In
# ----------------------------------------------------------------------
# Note: There's a distinction between database users (admin and client)
# and application users (e.g. members registered to a store). You can
# choose how to implement these depending on whether you have app.py or
# app-client.py vs. app-admin.py (in which case you don't need to
# support any prompt functionality to conditionally login to the sql database)
def login_as_admin():
    """
    Prompts an admininstrator to input their username and password.
    Checks whether or not the username and password is valid, otherwise
    quits out of interface.
    """
    username = input('Enter admin username: ')
    password = input('Enter admin password: ')
    cursor = conn.cursor()
    sql = 'SELECT authenticate(\'%s\', \'%s\');' % (username, password, )
    try:
        cursor.execute(sql)
        res = cursor.fetchone()
        if res[0]:
            return True
        else:
            return False
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('An error occurred while authenticating admin.')
            return

def login_as_user():
    """
    Prompts a user to input their username and password. Checks whether or
    not the username and password is valid. If the username does not exist
    in the database, create a new user in the user_info table.
    """
    username = input('Enter username: ')
    password = input('Enter password: ')
    if exists('user_info', 'username', username):
        cursor = conn.cursor()
        sql = 'SELECT authenticate(\'%s\', \'%s\')' % (username, password, )
        try:
            cursor.execute(sql)
            res = cursor.fetchone()
            if res[0]:
                return True
            else:
                return False
        except mysql.connector.Error as err:
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred while authenticating user.')
                return
    else:
        cursor = conn.cursor()
        sql = 'CALL sp_add_user(\'%s\', \'%s\')' % (username, password, )
        try:
            cursor.execute(sql)
            conn.commit()
            print('Added new user to database.')
            return True
        except mysql.connector.Error as err:
            if DEBUG:
                sys.stderr(err)
                sys.exit(1)
            else:
                sys.stderr('An error occurred while authenticating user.')
                return

# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
def show_user_options():
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    print('What would you like to do? ')
    print('  (w) - show tournament winners')
    print('  (t) - show players inside/outside top 20')
    print('  (s) - show number of matches played by surface')
    print('  (c) - view players by country')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'w':
        show_tournament_winners()
    elif ans == 't':
        show_players_top_20()
    elif ans == 's':
        show_surface_count()
    elif ans == 'c':
        show_player_country()
    else:
        print('Unknown option.')

def show_admin_options():
    """
    Displays options specific for admins, such as adding new data <x>,
    modifying <x> based on a given id, removing <x>, etc.
    """
    print('What would you like to do? ')
    print('  (u) - update player information')
    print('  (i) - input match results')
    print('  (r) - update player rankings')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'i':
        input_match_results()
    elif ans == 'u':
        update_player_information()
    elif ans == 'r':
        update_rankings()
    else:
        print('Unknown option.')


def quit_ui():
    """
    Quits the program, printing a good bye message to the user.
    """
    print('Good bye!')
    exit()


def login_options():
    """
    Displays options for logging in to the database as either an admin
    (e.g. tournament official) or user (e.g. fan or player).
    """
    print('How would you like to login? ')
    print('  (a) - admin')
    print('  (u) - user')
    ans = input('Enter either (a) or (u) for logging in: ').lower()
    if ans == 'a':
        if login_as_admin():
            conn = get_conn_for_admin()
            show_admin_options()
        else:
            print('Invalid admin login. Please try again.')
            quit_ui()
    elif ans == 'u':
        if login_as_user():
            conn = get_conn_for_user()
            show_user_options()
        else:
            print('Invalid user login. Please try again.')
            quit_ui()
    elif ans == 'q':
        quit_ui()
    else:
        print('Unknown option.')


def main():
    """
    Main function for starting things up.
    """
    login_options()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn_for_admin()
    main()
