#!/usr/bin/env bash
# Creates a database and user to use Devicehub
# $1 is the database to create
# $2 is the user to create and give full permissions on the database
# This script asks for the password of such user

read -s -p "Password for $2": pass
createdb $1  # Create main database
psql -d $1 -c "CREATE USER $2 WITH PASSWORD '$pass';" # Create user Devicehub uses to access db
psql -d $1 -c "GRANT ALL PRIVILEGES ON DATABASE $1 TO $2;" # Give access to the db
