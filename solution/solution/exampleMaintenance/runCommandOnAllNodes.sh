#!/bin/bash

# Run this script from a personal computer, not on one of your vms. 

command=$1

# Change directory to where the script is stored, not where it is run from
scriptPath=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $scriptPath

# We use a config file that has connection information for each node
# It should have the following variables
# chainName
# user
# password
# node_1_ip
# node_2_ip
# node_3_ip
# node_4_ip
source exampleConfig.sh

sshCommand="sshpass -p $password ssh -t -l $user -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

echo "Running command on node 1"
$sshCommand $node_1_ip "$command"
echo "Running command on node 2"
$sshCommand $node_2_ip "$command"
echo "Running command on node 3"
$sshCommand $node_3_ip "$command"
echo "Running command on node 4"
$sshCommand $node_4_ip "$command"

echo "Done running command on all nodes"
