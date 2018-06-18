#!/bin/bash

# script.sh dir_prefix num_of_node port [chain_name]

if (( $# < 3 )); then
    echo "format: script.sh dir_prefix num_of_node port [chain_name]"
    exit
fi

# check if jason parser exist
if ! [ -x "$(command -v jq)" ]; then
    echo "Cannot find jq. Please install jq."
    exit
fi   


dir_prefix=$1
num_of_node=$2
rpcport=$3
# if chain_name is specified
if (($# == 4)); then
    chain=$4
else
    chain=chain1
fi


echo rpcuser=multichainrpc >> multichain.conf
echo rpcpassword=emory >> multichain.conf
echo rpcallowip=0.0.0.0/0 >> multichain.conf
echo rpcport=$rpcport >> multichain.conf

# create folder for each node
for ((i=0; i < $num_of_node; i++))
do
    newdir=$(echo $dir_prefix$i)/multichain
    mkdir -p $newdir
    cp multichain.conf $newdir/
done    

rm multichain.conf

# run master node
dir=$(pwd)/${dir_prefix}0
docker run -it -d --name ${dir_prefix}0 -v $dir/multichain:/root/.multichain -p 2750:2750 -p $rpcport:$rpcport mshuaic/blockchainnode 

# create blockchain
docker exec -d ${dir_prefix}0 multichain-util create chain1 -default-rpc-port=$3 -default-network-port=$[$3+1] -mine-empty-rounds=1 -anyone-can-connect=true -anyone-can-create=true -anyone-can-send=true -anyone-can-receive=true -setup-first-blocks=1 -anyone-can-mine=true -mining-turnover=0 -target-block-time=2

# copy config file
docker exec -d ${dir_prefix}0 cp -f /root/.multichain/multichain.conf /root/.multichain/$chain/multichain.conf

# run blockchain
docker exec -d ${dir_prefix}0 multichaind $chain -autosubscribe=streams -daemon

# run multichain-explorer
# ATTENTION:
# if chain name is not chain1, configure multichain accordingly.
docker exec -d ${dir_prefix}0 python -m Mce.abe --config /root/multichain-explorer/chain1.conf

# docker network ip
ip=$(docker exec ${dir_prefix}0 hostname -I)
# blockchain connection port
conport=$[$rpcport + 1]

# run other nodes
for ((i=1; i < $num_of_node; i++))
do
    nodename=$dir_prefix$i
    docker run -it -d --name $nodename -v $(pwd)/$nodename/multichain:/root/.multichain -p $[$rpcport + $i]:$rpcport mshuaic/blockchainnode
    docker exec -d $nodename multichaind $chain@$ip:$conport -rpcpassword=emory -autosubscribe=streams -daemon

    # this setup is not good for multichain-explorer on slave nodes
    # docker exec -d $nodename cp -f /root/.multichain/multichain.conf /root/.multichain/$chain/multichain.conf
done

# pause for 1 s, let node start to run blockchain
sleep 1

# a workaround of this issue
# https://www.multichain.com/qa/3601/anyone-can-issue-dont-seem-to-work?show=3604#a3604
# get slaves' address and send 0 asset to them
for ((i=0; i< $num_of_node; i++))
do
    address[$i]=$(curl -d '{"method":"getaddresses","params":[]}' http://multichainrpc:emory@127.0.0.1:$[$rpcport + $i]/ 2>/dev/null | jq '.["result"][0]')
done

for ((i=1; i< $num_of_node; i++))
do
    curl -d '{"method":"send","params":['"${address[$i]}"',0]}' http://multichainrpc:emory@127.0.0.1:$rpcport/ 
done

# sleep 5

# for ((i=1; i< $num_of_node; i++))
# do
#     curl -d '{"method":"send","params":['"${address[0]}"',0]}' http://multichainrpc:emory@127.0.0.1:$[$rpcport+$i]/ 
# done


