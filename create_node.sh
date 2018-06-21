#!/bin/bash

#bash script.sh [dir_prefix] [num_of_node] [port] [chain_name]

dir_prefix=node
num_of_node=4
rpcport=8570
chain=chain1


if (( $# == 4 )); then
    echo "format: script.sh dir_prefix num_of_node port chain_name"
    dir_prefix=$1
    num_of_node=$2
    rpcport=$3
    chain=$4
fi

# check if jason parser exist
if ! [ -x "$(command -v jq)" ]; then
    echo "Cannot find jq. Please install jq."
    echo "https://stedolan.github.io/jq/" 
    exit
fi   


TIMEOUT=10

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
echo "building master node"
dir=$(pwd)/${dir_prefix}0
docker run -it -d --name ${dir_prefix}0 -v $dir/multichain:/root/.multichain -p 2750:2750 -p $rpcport:$rpcport mshuaic/blockchainnode 1>/dev/null

# create blockchain
docker exec -d ${dir_prefix}0 multichain-util create $chain -default-rpc-port=$rpcport -default-network-port=$[$rpcport+1] -mine-empty-rounds=1 -anyone-can-connect=true -anyone-can-create=true -anyone-can-send=true -anyone-can-receive=true -setup-first-blocks=1 -anyone-can-mine=false -mining-turnover=0 -target-block-time=2

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
echo "building slave nodes"
for ((i=1; i < $num_of_node; i++))
do
    nodename=$dir_prefix$i
    docker run -it -d --name $nodename -v $(pwd)/$nodename/multichain:/root/.multichain -p $[$rpcport + $i]:$rpcport mshuaic/blockchainnode 1>/dev/null
    docker exec -d $nodename multichaind $chain@$ip:$conport -rpcpassword=emory -autosubscribe=streams -daemon

    # this setup is not good for multichain-explorer on slave nodes
    # docker exec -d $nodename cp -f /root/.multichain/multichain.conf /root/.multichain/$chain/multichain.conf
done

# pause for 1 s, let node start to run blockchain
echo "setting up nodes"
sleep 2

# a workaround of this issue
# https://www.multichain.com/qa/3601/anyone-can-issue-dont-seem-to-work?show=3604#a3604
# get slaves' address and send 0 asset to them
confirmation=0
until ((confirmation >= 1))
do
    echo "send 0 asset to slave"
    for ((i=0; i< $num_of_node; i++))
    do
	address[$i]=$(curl -d '{"method":"getaddresses","params":[]}' http://multichainrpc:emory@127.0.0.1:$[$rpcport + $i]/ 2>/dev/null | jq '.["result"][0]')
	# echo ${address[$i]}
    done
    
    for ((i=1; i< $num_of_node; i++))
    do
	txid[$i]=$(curl -d '{"method":"send","params":['"${address[$i]}"',0]}' http://multichainrpc:emory@127.0.0.1:$rpcport/ 2>/dev/null | jq '.["result"]') 
	# echo ${txid[$i]}
    done
    
    for ((i=1; i< $num_of_node; i++))
    do
	timer=0
	confirmation=0
	until (( $confirmation >= 1 ))
	do
	    confirmation=$(curl -d '{"method":"gettxout","params":['"${txid[$i]}"',0]}' http://multichainrpc:emory@127.0.0.1:$rpcport/ 2>/dev/null | jq '.["result"]["confirmations"]')
	    sleep 1
	    ((timer++))
	    if ((timer == TIMEOUT)); then
		echo "TIME OUT"
		break
	    fi
	done
	if ((timer == TIMEOUT)); then
	    break
	fi
    done    
done

# for ((i=1; i< $num_of_node; i++))
# do
#     timer=0
#     confirmation=0
#     until (( $confirmation >= 1 ))
#     do
# 	confirmation=$(curl -d '{"method":"gettxout","params":['"${txid[$i]}"',0]}' http://multichainrpc:emory@127.0.0.1:$rpcport/ 2>/dev/null | jq '.["result"]["confirmations"]')
# 	sleep 1
# 	((timer++))
# 	if ((timer == TIMEOUT)); then
# 	   echo "TIME OUT"
# 	   exit
# 	fi
#     done
# done

echo "nodes and blockchain are successfully created"
