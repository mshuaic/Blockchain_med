#!/bin/bash

# DESCRIPTION GOES HERE

cd ~/.multichain

for chainName in *; do
    if [ -d "${chainName}" ]; then
    	echo "Stopping $chainName"
    	chainPid=$(cat $chainName/multichain.pid)
    	multichain-cli "$chainName" stop
    	while kill -0 "$chainPid"; do
		    sleep 0.5
		done
		echo "Deleting $chainName"
    	rm -rf "$chainName"
    	echo "Done"
    fi
done