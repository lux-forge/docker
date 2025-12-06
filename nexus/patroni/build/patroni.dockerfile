FROM postgres:17-alpine as postgres-patroni

# Install Patroni dependencies
RUN apk add --no-cache build-base linux-headers python3-dev py3-pip py3-virtualenv su-exec bash

# Create a virtual environment
RUN python3 -m venv /venv && mkdir /venv/etc
WORKDIR /venv

# Install Patroni and psycopg2
RUN /venv/bin/pip install patroni[etcd] psycopg2

# Copy entrypoint script
COPY patroni-entrypoint.sh /usr/local/bin/patroni-entrypoint.sh
RUN chmod +x /usr/local/bin/patroni-entrypoint.sh

# Use absolute path for entrypoint
ENTRYPOINT ["/usr/local/bin/patroni-entrypoint.sh"]

# Document ports (hardcode for now)
EXPOSE 5432 8008 5433 2379

# Start Patroni
CMD ["/venv/bin/patroni", "/venv/etc/patroni.yml"]