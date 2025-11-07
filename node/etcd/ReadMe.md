## ETCD cluster

Provides a single node to be attached to other nodes. Env variables to use:

in .env file:

```

ETCD1_NAME=[Name of first ETCD server]
ETCD2_NAME=[Name of second ETCD server]
ETCD3_NAME=[Name of third ETCD server]
ETCD_NAME=[Reference back to ETC#_Name for this particular node]

ETCD1_IP=[IP address of first ETCD server]
ETCD2_IP=[IP address of first ETCD server]
ETCD3_IP=[IP address of first ETCD server]
ETCD_IP=[Reference back to ETC#_IP for this particular node]

ETCD_INITIAL_CLUSTER=${ETCD1_Name}=http://${ETCD1_IP}2380,${ETCD2_Name}=http://${ETCD2_IP}:2380,${ETCD3_Name}=http://${ETCD3_IP}:2380

ETCD_INITIAL_CLUSTER_TOKEN=[Name of the token]
ETCD_DATA_DIR=[Location of data]
ETCD_INITIAL_ADVERTISE_PEER_URLS=http://$[ETCD_IP]:2380
ETCD_LISTEN_PEER_URLS=http://0.0.0.0:2380
ETCD_LISTEN_CLIENT_URLS=http://0.0.0.0:2379
ETCD_ADVERTISE_CLIENT_URLS=http://$[ETCD_IP]:2379
ETCD_INITIAL_CLUSTER_STATE=new
```