# LUXFORGE Docker

The purpose of this is to provide my homelab docker setup as a single repo, applicable to all hosts. 

### Nodes
This folder hosts docker builds that are only appropriate for one node at a time; such as a media server

### Nexus
The idea of this is LuxForge's own flavour of swarm or clustering. Each node hosts all items in the nexus with their own env config. This is to enable HA and resiliency despite any of the nodes going offline.
