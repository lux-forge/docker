FROM postgres:alpine as postgres-patroni

# Install Patroni dependencies
RUN apk update && \
    apk add --update --no-cache \
    build-base \
    linux-headers \
    python3-dev \
    py3-pip \
    py3-virtualenv \
    su-exec && \
    python3 -m venv /venv && \
    mkdir /venv/etc

# Create a virtual environment
# RUN python3 -m venv /venv && mkdir /venv/etc

# Install Patroni
# prima mi metto nel punto
WORKDIR /venv
# RUN /venv/bin/pip install patroni[etcd]
# diventa
RUN ./bin/pip install psycopg2 && ./bin/pip install patroni[etcd]

# Set the working directory to the PostgreSQL home directory
WORKDIR /var/lib/postgresql

# Copy your custom entrypoint script into the container
COPY patroni-entrypoint.sh /usr/local/bin/patroni-entrypoint.sh

# Make sure the script is executable
RUN chmod +x /usr/local/bin/patroni-entrypoint.sh

# Start Patroni su entry point
ENTRYPOINT ["patroni-entrypoint.sh"]

# Expose ports for PostgreSQL and Patroni's REST API
EXPOSE 5432 
EXPOSE 8008