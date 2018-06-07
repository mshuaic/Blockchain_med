from Savoir import Savoir
import re

# node0 rpc credential
node0 = {
    "rpcuser": 'multichainrpc',
    "rpcpasswd": 'F7ZnmKHnA3GWX68DoGSyAWfG9xmp6Kj3d3btjLZNLmo4',
    "rpcport": '4394',
    "rpchost": '34.202.165.15',
    "chainname": 'chain1'
}

# node1 rpc credential
node1 = {
    "rpcuser": 'multichainrpc',
    "rpcpasswd": '5wJGtHcdCLXsVYXuMBXicmxV6VqhWxFE1PwMLuGEcoPk',
    "rpcport": '8001',
    "rpchost": '34.202.165.15',
    "chainname": 'chain1'
}

# connect to nodes
api0 = Savoir(node0["rpcuser"], node0["rpcpasswd"],
              node0["rpchost"], node0["rpcport"], node0["chainname"])
api1 = Savoir(node1["rpcuser"], node1["rpcpasswd"],
              node1["rpchost"], node1["rpcport"], node1["chainname"])
# print(api0.getinfo())
# print(api1.getinfo())


# api0.create('stream', 'stream1', True)
# api0.liststreams('stream1')
# api1.liststreams('stream1')


api0.subscribe('stream1')
api1.subscribe('stream1')

# read log file
lines = [re.sub('\s+', ' ', line) for line in open('test1.txt')]
# print(lines)
# for line in lines:
# print(line)
# api0.publish('stream1', 'node0', line.encode('utf-8').hex())

for item in api1.liststreamkeyitems('stream1', 'node0'):
    print(bytes.fromhex(item['data']).decode('utf-8'))
