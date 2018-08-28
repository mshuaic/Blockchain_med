#!/bin/bash

nodes=("172.17.0.2" "172.17.0.3" "172.17.0.4" "172.17.0.5")

for node in "${nodes[@]}"
do
    sshpass -p root scp -r * root@$node:~
done

