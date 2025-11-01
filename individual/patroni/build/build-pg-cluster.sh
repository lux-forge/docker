#! /bin/bash

etcd_env=/tmp/test

# Remove any old env files
rm "$etcd_env"

# Cast new file
cp etcdenv "$etcd_env"

# Export the env variables to the file

source ./env.d/charlemagne.env
source ./env.d/main.env

cat <<EOF >> "$etcd_env"
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://${NODE_IP}:${ETCD_PEER_PORT}"
ETCD_ADVERTISE_CLIENT_URLS="https://${NODE_IP}:${ETCD_CLIENT_PORT}"
ETCD_NAME="${PG_CLUSTER_NAME}"
ETCD_INITIAL_CLUSTER="${PG_CLUSTER_NAME}=https://${NODE_IP}:${ETCD_PEER_PORT},${PG_CLUSTER_NEIGHBOUR1_NAME}=https://${PG_CLUSTER_NEIGHBOUR1_IP}:${ETCD_PEER_PORT},${PG_CLUSTER_NEIGHBOUR2_NAME}=https://${PG_CLUSTER_NEIGHBOUR2_IP}:${ETCD_PEER_PORT}"
EOF

# Run the etcd server
etcd-server