#!/usr/bin/env bash
# Creates a database, user, and extensions to use Tag

createdb $1  # Create main database
psql -d $1 -c "CREATE USER dtag WITH PASSWORD 'ereuse';" # Create user dtag uses to access db
psql -d $1 -c "GRANT ALL PRIVILEGES ON DATABASE $1 TO dhub;" # Give access to the db
