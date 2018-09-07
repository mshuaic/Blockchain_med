#!/bin/bash

chainName='testChain';

cd ~/.multichain/${chainName}
source multichain.conf
# Now the following varialbles are set
# $rpcusername
# $rpcpassword

rpcport=$(awk '/^default-rpc-port/{print $3}' params.dat)

streams=('T' 'N' 'I' 'F' 'U' 'A' 'R' 's4' 's6' 's8')
