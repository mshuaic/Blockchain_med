#!/bin/bash

# chainName='testChain';
chainName='chain1';

cd ~/.multichain/${chainName}
source multichain.conf
# Now the following varialbles are set
# $rpcusername
# $rpcpassword

rpcport=$(awk '/^default-rpc-port/{print $3}' params.dat)

streams=('Timestamp' 'Node' 'ID' 'Ref-ID' 'User' 'Activity' 'Resource' 'ts10000')
