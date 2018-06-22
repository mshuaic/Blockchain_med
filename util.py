from Savoir import Savoir
from timeit import default_timer as timer
from config import *

ENCODE_FORMAT = 'utf-8'


def getAPI(config, num_node):
    api = [None] * num_node
    for i in range(NUM_NODE):
        api[i] = Savoir(config["rpcuser"], config["rpcpasswd"],
                        config["rpchost"], str(config["rpcport"]+i), config["chainname"])
    # print(api[i].getinfo())
    return api


def createStream(masternode, streamPrefix):
    streams = masternode.liststreams()['result']
    if streamPrefix not in [item["name"] for item in streams]:
        masternode.create('stream', streamPrefix, True)
    # for i in range(NUM_NODE):
    # api[i].create('stream', 'node'+str(i), True)


def measure(func, args, time=1):
    elapsed = timer()
    for i in range(time):
        func(*args)
    elapsed = timer() - elapsed
    # print("average insertion time: %f" % (elapsed / time))
    return elapsed / time


def display(result):
    for item in result:
        print(bytes.fromhex(item['data']).decode(ENCODE_FORMAT))


def getData(result, isHex=False):
    data = []
    for item in result:
        if isHex:
            data.append(item['data'])
        else:
            data.append(bytes.fromhex(item['data']).decode(ENCODE_FORMAT))
    return data
