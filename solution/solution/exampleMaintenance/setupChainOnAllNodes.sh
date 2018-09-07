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

echo "Ensuring setup scripts are executable"
$sshCommand $node_1_ip "chmod 774 setup*"
$sshCommand $node_2_ip "chmod 774 setup*"
$sshCommand $node_3_ip "chmod 774 setup*"
$sshCommand $node_4_ip "chmod 774 setup*"

echo "Setting up primary node"
$sshCommand $node_1_ip "~/setupChainOnPrimaryNode.sh 2>&1 | tee setup.log"
echo "Setting up node 2"
$sshCommand $node_2_ip "~/setupChain.sh 2>&1 | tee setup.log"
echo "Setting up node 3"
$sshCommand $node_3_ip "~/setupChain.sh 2>&1 | tee setup.log"
echo "Setting up node 4"
$sshCommand $node_4_ip "~/setupChain.sh 2>&1 | tee setup.log"

echo "Done"