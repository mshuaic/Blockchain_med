from Savoir import Savoir
import re

NUM_NODE = 4

rpc = {
    # "node": {
    #     0: {
    #         "rpcpasswd": 'EfPdYnjY6D8YQrNkxXBzTpXbpvpGiccG3FZH4MFcYcPu',
    #         "rpcport": '8570'
    #     },
    #     1: {
    #         "rpcpasswd": '9y6DrxQd3ACkjDCLMSNoE37vADeGdPh64UM44kt8DYhy',
    #         "rpcport": '8571'
    #     },
    #     2: {
    #         "rpcpasswd": 'BkrnZHxunHcPMoqAKpdZsihzvyHKbueXxBpLhaPFqbYt',
    #         "rpcport": '8572'
    #     },
    #     3: {
    #         "rpcpasswd": 'Bj3VYGpE17NWYrkVUuCm2nW1r3HswipKbkuiXRjYMzTE',
    #         "rpcport": '8573'
    #     }

    # },
    "rpcuser": 'multichainrpc',
    "rpcpasswd": 'emory',
    "rpchost": '127.0.0.1',
    "rpcport": 8570,
    "chainname": 'chain1'
}


api = [None] * NUM_NODE

for i in range(NUM_NODE):
    api[i] = Savoir(rpc["rpcuser"], rpc["rpcpasswd"],
                    rpc["rpchost"], str(rpc["rpcport"]+i), rpc["chainname"])
    print(api[i].getinfo())
    # print(api[i].getaddresses()[0])
    # rpc["node"][i]["address"] = api[i].getaddresses()[0]
# print(api[0].getaddresses()[0])

# a workarount of this issue
# https://www.multichain.com/qa/3601/anyone-can-issue-dont-seem-to-work?show=3604#a3604
# for i in range(1, NUM_NODE):
    # api[0].grant(rpc["node"][i]["address"], "receive")
    # api[0].send(rpc["node"][i]["address"], 0)

# for i in range(1, NUM_NODE):
    # api[0].grant(rpc["node"][i]["address"], "send")

# for i in range(NUM_NODE):
    # api[i].send(rpc["node"][0]["address"], 0)
    # api[i].create('stream', 'node'+str(i), True)


# for i in range(NUM_NODE):
#     for j in range(NUM_NODE):
#         api[i].subscribe('node'+str(j))


# read log file
# # print(lines)
# # for line in lines:
# # print(line)
# # api0.publish('stream1', 'node0', line.encode('utf-8').hex())

# for item in api1.liststreamkeyitems('stream1', 'node0'):
#     print(bytes.fromhex(item['data']).decode('utf-8'))

# lines = [re.sub('\s+', ' ', line) for line in open('test1.txt')]
# for line in lines:
#     print(line.split(" ")[0])


# for i in range(NUM_NODE):
    # lines = [re.sub('\s+', ' ', line) for line in open('test'+str(i+1)+'.txt')]
    # for line in lines:
    # for j in range(2, 7):
    # api[i].publish('node'+str(i), line.split(" ")
    # [j], line.encode('utf-8').hex())

# for e in api[0].liststreamitems('node3', False, 100):
#     print(bytes.fromhex(e['data']).decode('utf-8'))

# print("query one record")
# set1 = set()
# for e in api[0].liststreamkeyitems('node3', 'FILE_ACCESS'):
#     # print(bytes.fromhex(e['data']).decode('utf-8'))
#     set1.add(bytes.fromhex(e['data']).decode('utf-8'))

# set2 = set()
# for e in api[0].liststreamkeyitems('node3', 'MOD_SGD'):
#     # print(bytes.fromhex(e['data']).decode('utf-8'))
#     set2.add(bytes.fromhex(e['data']).decode('utf-8'))

# print("query 'FILE_ACCESS' and 'MOD_SGD'")
# for s in set1 & set2:
#     print(s)

# print("done")
