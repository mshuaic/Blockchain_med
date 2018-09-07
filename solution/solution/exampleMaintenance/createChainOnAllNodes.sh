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

echo "Creating primary node"
createOutput=$($sshCommand $node_1_ip "multichain-util create $chainName")

# -t is needed to make it exit
# -shortoutput returns only the connection string
echo "Starting primary node"
connectString=$($sshCommand $node_1_ip "multichaind $chainName -shortoutput -daemon" | tr -d '\r')

connectCommand="multichaind $connectString -shortoutput"


echo "Granting permissions to node 2"
node_2_walletAddress=$($sshCommand $node_2_ip "$connectCommand" | tr -d '\r')
node_2_grantResult=$($sshCommand $node_1_ip "multichain-cli $chainName grant $node_2_walletAddress connect,send,receive,issue,create,mine,activate,admin")
echo "Granting permissions to node 3"
node_3_walletAddress=$($sshCommand $node_3_ip "$connectCommand" | tr -d '\r')
node_3_grantResult=$($sshCommand $node_1_ip "multichain-cli $chainName grant $node_3_walletAddress connect,send,receive,issue,create,mine,activate,admin")
echo "Granting permissions to node 4"
node_4_walletAddress=$($sshCommand $node_4_ip "$connectCommand" | tr -d '\r')
node_4_grantResult=$($sshCommand $node_1_ip "multichain-cli $chainName grant $node_4_walletAddress connect,send,receive,issue,create,mine,activate,admin")

echo "Starting Node 2"
node_2_connectResult=$($sshCommand $node_2_ip "$connectCommand -daemon" | tr -d '\r')
echo "Starting Node 3"
node_3_connectResult=$($sshCommand $node_3_ip "$connectCommand -daemon" | tr -d '\r')
echo "Starting Node 4"
node_4_connectResult=$($sshCommand $node_4_ip "$connectCommand -daemon" | tr -d '\r')

echo "Done"
