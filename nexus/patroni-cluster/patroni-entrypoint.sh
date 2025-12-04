#!/bin/bash

echo "PostgreSQL wait for patroni to start. DB_NAME=$DB_NAME. DB_USER:$DB_USER"

# If you decide not to start PostgreSQL, you can keep the container running with:
# exec tail -f /dev/null
#
# Initialize PostgreSQL data directory (if not already initialized)
# Force ownershop of postgres db to venv user
echo "Setting user permissions on /var/lib/postrgresql/data"
chown postgres:postgres /var/lib/postgresql/data


if [ ! -d "/var/lib/postgresql/data" ]; then
    echo "No DB set. Creating one now"
    mkdir -p /var/lib/postgresql/data
    chown postgres:postgres /var/lib/postgresql/data
    su-exec postgres initdb -D /var/lib/postgresql/data
    set -e

su-exec postgres psql -v ON_ERROR_STOP=1 --username "$DB_USER" --dbname "$DB_NAME" <<-EOSQL
    CREATE DATABASE ${DB_NAME};
    GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOSQL
fi


echo "Running Patroni"
# Start Patroni
su-exec postgres /venv/bin/patroni /venv/etc/patroni.yml