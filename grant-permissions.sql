-- Grants permissions to either admins or users to the WTA database.

CREATE USER 'appadmin'@'localhost' IDENTIFIED BY 'adminpw';
CREATE USER 'appclient'@'localhost' IDENTIFIED BY 'clientpw';
-- Can add more users or refine permissions
GRANT ALL PRIVILEGES ON wtadb.* TO 'appadmin'@'localhost';
GRANT SELECT ON wtadb.* TO 'appclient'@'localhost';
FLUSH PRIVILEGES;
