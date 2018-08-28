#!/bin/bash

# node1="172.17.0.2"
# node2="172.17.0.3"
# node3="172.17.0.4"
# node4="172.17.0.5"

# sshCommand="sshpass -p root ssh -t -l root"
# $sshCommand $node1 "nohup ~/setupChainOnPrimaryNode.sh 2>&1 setup.log"
# $sshCommand $node2 "nohup ~/setupChain.sh 2>&1 setup.log"
# $sshCommand $node3 "nohup ~/setupChain.sh 2>&1 setup.log"
# $sshCommand $node4 "nohup ~/setupChain.sh 2>&1 setup.log"


master="172.17.0.2"
slaves=("172.17.0.3" "172.17.0.4" "172.17.0.5")
nodes=($master "${slaves[@]}")
sshCommand="sshpass -p root ssh -t -l root"

$sshCommand $master "nohup ~/setupChainOnPrimaryNode.sh 2>&1 setup.log"
for node in "${slaves[@]}"
do
    $sshCommand $node "nohup ~/setupChain.sh 2>&1 setup.log"
done

# for ((i=0;i<${#nodes[@]};i++))
# do
#     # echo ${nodes[i]}
#     # echo "training$[$i+1].txt &"
#     $sshCommand ${nodes[i]} "nohup ~/insert.sh --file Data/training$[$i+1].txt > /dev/null 2>&1" & 
# done
