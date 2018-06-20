# version 0.1
# 06/20/2018
# baseline implematation
# Insertion: insert n (n = number of attribute) times copy to blockchain, using attribute as key and entire line as value
# Range query: query from start time, and increase timestamp by 1 every time till end time. The total number of query needed is (start - end)
# And operation: query using single attribute and do AND operation locally


############################################################################
############################################################################


# Put data in the same directory


from Savoir import Savoir
import re
from time import sleep
from timeit import default_timer as timer
from random import randint
from random import gauss
from random import sample
import subprocess

NUM_NODE = 4


config = {
    "rpcuser": 'multichainrpc',
    "rpcpasswd": 'emory',
    "rpchost": '127.0.0.1',
    "rpcport": 8570,
    "chainname": 'chain1'
}

# time, node, ID, ref-ID, user, activity, resource
ATTRIBUTE = ['T', 'N', 'I', 'r', 'U', 'A', 'R']


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
        print(bytes.fromhex(item['data']).decode('utf-8'))


def getData(result):
    data = []
    for item in result:
        data.append(bytes.fromhex(item['data']).decode('utf-8'))
    return data


#########################################################################
######################       TEST        ################################
#########################################################################


STREAM = 'data'


def insert(api, data):
    for line in data:
        hexstr = line.encode('utf-8').hex()
        attributes = line.split(" ")
        for i in range(len(ATTRIBUTE)):
            api.publish(STREAM, ATTRIBUTE[i] + attributes[i], hexstr)


def singleQuery(api, attribute, display=False):
    result = api.liststreamkeyitems(STREAM, attribute)
    if display:
        display(result["result"])
    return result["result"]


def rangeQuery(api, start, end, display=False):
    result = []
    for timestamp in range(start, end+1):
        result += api.liststreamkeyitems(STREAM, 'T'+str(timestamp))
    if display:
        display(result["result"])


def andQuery(api, attributes, display=False):
    resultSet = []
    for attr in attributes:
        # print(getData(singleQuery(api, attr)))
        resultSet.append(set(getData(singleQuery(api, attr))))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    if display:
        display(result)


size = sum(1 for line in open('test0.txt'))
database = []
for i in range(NUM_NODE):
    database += [re.sub('\s+', ' ', line)
                 for line in open('test'+str(i)+'.txt')]
print("database size: %d" % len(database))

nodes = getAPI(config, NUM_NODE)
createStream(nodes[0], STREAM)
sleep(1)

print("File Size: %d\n" % size)


def insertionTest():
    print("Insertion Test:")
    total = 0
    for i in range(NUM_NODE):
        data = [re.sub('\s+', ' ', line)
                for line in open('test'+str(i)+'.txt')]
        elapsed = measure(insert, (nodes[i], data))
        total += elapsed
        print('Node %d Insertion time: %f' % (i, elapsed))
    print("total insertion time: %f " % total)
    print("average insertion time: %f" % (total/NUM_NODE))


def singleQueryTest():
    print("Single Field Query Test:")
    samplePer = 1
    sampleNum = len(database) * samplePer
    total = 0
    for i in range(NUM_NODE):
        elapsed = 0
        for j in range(sampleNum):
            index = randint(0, len(database)-1)
            line = database[index]
            field = randint(0, len(ATTRIBUTE)-1)
            elapsed += measure(singleQuery,
                               (nodes[i], ATTRIBUTE[field] + line.split(" ")[field]))
        total += elapsed
        print("Node %d query time: %f" % (i, elapsed / sampleNum))
    print("average query time: %f" % (total/(sampleNum * NUM_NODE)))


def rangeQueryTest():
    print("Range Query Test:")
    EPOCH_BEGIN = 1522000000000
    EPOCH_END = 1523000000000
    RANGE = (EPOCH_END - EPOCH_BEGIN) / 1000000  # e8
    NUM_TEST = 1

    total = 0
    for i in range(NUM_NODE):
        start = randint(EPOCH_BEGIN, EPOCH_END)
        timeRange = int(gauss(0, 0.1) * RANGE / 2 + RANGE / 2)
        print("timeRange: %ds(min: %.2f)" % (timeRange, timeRange/60))
        elapsed = 0
        for j in range(NUM_TEST):
            elapsed += measure(rangeQuery, (nodes[i], start, start+timeRange))
        print("node %d range query time: %f" % (i, elapsed/NUM_TEST))
        total += elapsed/NUM_TEST
    print("average range query time: %f" % (total / NUM_NODE))


def andQueryTest():
    print("And Query Test:")
    NUM_TEST = 1
    for i in range(NUM_NODE):
        index = randint(0, len(database)-1)
        line = database[index]
        elapsed = 0
        for k in range(NUM_TEST):
            attributes = []
            for j in range(2, len(ATTRIBUTE)):
                fields = sample(range(len(ATTRIBUTE)), j)
                for q in range(len(fields)):
                    attributes.append(
                        ATTRIBUTE[fields[q]] + line.split(" ")[fields[q]])
                andQueryTime = measure(andQuery, (nodes[i], attributes))
                elapsed += andQueryTime
                print("%d and query: %f" % (j, andQueryTime))
        print("node %d and query time: %f" % (i, elapsed/NUM_TEST))


def storageTest():
    print("Storage Usage:")
    print(subprocess.call(['sudo', 'du', '-sh', '-Bk',
                           'node0', 'node1', 'node2', 'node3']))


##########################################################################
########################         MAIN       ##############################
##########################################################################


insertionTest()
print("\n")
singleQueryTest()
print("\n")
rangeQueryTest()
print("\n")
andQueryTest()
print("\n")
storageTest()
