#! /bin/bash

etcd-server

etcd_env=/tmp/test

# Remove any old env files
rm $etcd_env

# Cast new file
cp etcdenv $etcd_env

# Export the env variables to the file
etcd_str='ETCD_INITIAL_ADVERTISE_PEER_URLS="https://'$PG_CLUSTER_IP':2380"\n'
etcd_str=$etcd_str'ETCD_ADVERTISE_CLIENT_URLS="https://'$PG_CLUSTER_IP':2379"\n'
etcd_str=$etcd_str'ETCD_NAME="'$PG_CLUSTER_NAME'"\n'
etcd_str=$etcd_str'ETCD_INITIAL_CLUSTER="'$PG_CLUSTER_NAME'=https://'$PG_CLUSTER_IP':2380,'$PG_CLUSTER_NEIGHBOUR1_NAME'=https://'$PG_CLUSTER_NEIGHBOUR1_IP':2380,'$PG_CLUSTER_NEIGHBOUR2_NAME'=https://'$PG_CLUSTER_NEIGHBOUR2_IP':2380"' 
echo $etcd_str >> $etcd_env