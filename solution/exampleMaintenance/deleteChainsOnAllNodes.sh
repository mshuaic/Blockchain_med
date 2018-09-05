#!/bin/bash

# Run this script from a personal computer, not on one of your vms. 

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

echo "Ensuring delete script is executable"
$sshCommand $node_1_ip "chmod 774 ~/exampleMaintenance/deleteChains.sh"
$sshCommand $node_2_ip "chmod 774 ~/exampleMaintenance/deleteChains.sh"
$sshCommand $node_3_ip "chmod 774 ~/exampleMaintenance/deleteChains.sh"
$sshCommand $node_4_ip "chmod 774 ~/exampleMaintenance/deleteChains.sh"

echo "Deleting chains on node 1"
$sshCommand $node_1_ip "~/exampleMaintenance/deleteChains.sh"
echo "Deleting chains on node 2"
$sshCommand $node_2_ip "~/exampleMaintenance/deleteChains.sh"
echo "Deleting chains on node 3"
$sshCommand $node_3_ip "~/exampleMaintenance/deleteChains.sh"
echo "Deleting chains on node 4"
$sshCommand $node_4_ip "~/exampleMaintenance/deleteChains.sh"

echo "Done deleting chains on all nodes"
