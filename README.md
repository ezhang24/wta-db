This is our final project for CS 121 Relational Databases at Caltech.
The goal of this project was to create a database that stored WTA information
such as players, recent match results, tournaments, and tournament histories.
The database supports a certain number of command-line queries with admin
and user logins.

**Contributors:** Emily Zhang, Bea Avila-Rimer

**Data source:** https://github.com/JeffSackmann/tennis_wta

## Getting Started
**Instructions for loading data on command-line:**
Make sure you have MySQL downloaded and available through your
device's command-line.

First, create an appropriate database in MySQL:
```
mysql> CREATE DATABASE wtadb;
mysql> USE wtadb;
```
Not including the `mysql>` prompt, run the following lines of code on your command-line
after creating and using an appropriate database:
```
mysql> source setup.sql;
mysql> source load-data.sql;
mysql> source setup-passwords.sql;
mysql> source setup-routines.sql;
mysql> source grant-permissions.sql;
mysql> source queries.sql;
```
**Instructions for Python program:**
Please install the Python MySQL Connector using `pip3` if not installed already.

After loading the data and verifying you are in the correct database,
run the following to open the python application:
```
mysql> quit;
$ python app.py
```
Please log in with the following user/passwords:

For users, the following usernames are registered:
| User     | Password |
|----------|----------|
| elzhang  | emily123 |
| bavilari | bea123   |

For admin, the following admin usernames are registered:
| User     | Password |
|----------|----------|
| admin    | adminpw  |

*Here is a suggested guide to using the app as a user:*
1. Select option [w] to show past tournament winners.
2. Select option [t] to show players inside or outside the top 20!
3. Select option [s] to show the number of matches played by surface for a specific player.
4. Select option [c] to view players from a specified country.

*Here is a suggested guide to using the app as an admin:*
1. Select option [u] to update player information.
2. Select option [i] to input match results.
3. Select option [r] to update the current top 20 WTA rankings.

In future iterations, we would add more options for both the
user and admin. We would also separate the user interface into one
for fans and one for players such that they can access different options
catered towards the respective user.
