#!/bin/bash
set -e

# get a timestamp
timestamp() {
  date +"%Y-%m-%d %T"
}

echo "$(timestamp): Ensuring permissions on /var/lib/postgresql/data"

if [ ! -d "/var/lib/postgresql/data" ]; then
  echo "$(timestamp): /var/lib/postgresql/data does not exist. Creating now."
  mkdir -p /var/lib/postgresql/data
fi

chown -R postgres:postgres /var/lib/postgresql/data
chmod 700 /var/lib/postgresql/data

echo "$(timestamp): Starting Patroni"
exec su-exec postgres /venv/bin/patroni /venv/etc/patroni.yml