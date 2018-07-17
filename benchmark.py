# version 0.3
# 06/26/2018
# use fixed query to benchmark
# added graphic chart

# version 0.2.1
# 06/25/2018
# added validation function

# version 0.2
# 06/21/2018
# implematation hash pointer

# version 0.11
# 06/21/2018
# clean up the code

# 06/20/2018
# baseline implematation
# Insertion: insert n (n = number of attribute) times copy to blockchain, using attribute as key and entire line as value
# Range query: query from start time, and increase timestamp by 1 every time till end time. The total number of query needed is (start - end)
# And operation: query using single attribute and do AND operation locally


###########################################################################
###########################################################################

import re
import json
# from time import sleep
from random import sample
from util import measure, getAPI
import util
from config import NUM_NODE, FILE_SIZE, datadir, config, ATTRIBUTE, ATTRIBUTE_NAME
from pathlib import Path
import logging
from itertools import combinations

#########################################################################
######################   implematation file   ###########################
#########################################################################

# from baseline0_2 import *
# import baseline0_2 as baseline
import importlib
baseline = None


def loadBaseline(file):
    global baseline
    baseline = importlib.import_module(file)


#########################################################################
######################       benchmark        ###########################
#########################################################################

TESTCASE_CONFIG = {
    "pointQuery": 8,
    "rangeQuery": 1,
    "andQuery": 1
}
RANGE_SCALE = [100, 500, 1000]
AND_FIELDS = ATTRIBUTE_NAME

MAX_ROUND = 50

output_json = {'num_nodes': NUM_NODE, 'file_size': FILE_SIZE, 'insertion': 0,
               'point_query': {}, 'range_query': {}, 'and_query': {}, 'storage': 0}

dir_path = Path.cwd()
log = logging.getLogger("benchmark")
log.setLevel('INFO')
# log.setLevel('DEBUG')

nodes = None
database = util.database
testcases = {key: [] for key in TESTCASE_CONFIG}
index = 0


def init():
    if baseline is None:
        log.error("Please call loadBaseline() to load baseline first")
        exit

    # size = sum(1 for line in open(datadir+'test0.txt'))
    database.buildFromFiles([Path(datadir).joinpath(
        'test'+str(i)+'.txt') for i in range(NUM_NODE)])
    log.info("database size: %d", len(database))

    global nodes
    nodes = getAPI(config, NUM_NODE)
    baseline.createStreams(nodes[0])

    log.info("File Size: %d" % FILE_SIZE)


def loadTestCases(testfile='testcases.json'):
    global testcases
    temp = [database[i]
            for i in sample(range(len(database)), sum(TESTCASE_CONFIG.values()))]
    # print(temp)
    count = 0
    if Path(Path(dir_path).joinpath(testfile)).is_file() is False:
        for key in TESTCASE_CONFIG.keys():
            for i in range(TESTCASE_CONFIG[key]):
                testcases[key].append(temp[count])
                count += 1
        with open(testfile, 'w') as write_file:
            json.dump(testcases, write_file)
    else:
        with open(testfile, 'r') as read_file:
            testcases = json.load(read_file)


def insertionTest():
    log.info("Insertion Test:")
    total = 0
    for i in range(NUM_NODE):
        data = [re.sub('\s+', ' ', line)
                for line in open(Path(datadir).joinpath('test'+str(i)+'.txt'))]
        elapsed = measure(baseline.insert, nodes[i], data)
        total += elapsed
        log.info('Node %d Insertion time: %f' % (i, elapsed))
    log.info("total insertion time: %f " % total)
    log.info("average insertion time: %f" % (total/NUM_NODE))
    output_json['insertion'] = total/NUM_NODE


def getAverageNodeRound(func, *args, rounds=MAX_ROUND):
    elapsed = 0
    # log.debug(args)
    for i in range(rounds):
        for j in range(NUM_NODE):
            elapsed += measure(func, nodes[j], *args)
    return elapsed / (rounds * NUM_NODE)


def pointQueryTest():
    log.info("Point Field Query Test:")
    i = 0
    total = 0
    for i in range(len(ATTRIBUTE)):
        elapsed = 0
        fields = testcases['pointQuery'][i].split(" ")
        qtime = getAverageNodeRound(baseline.pointQuery,
                                    ATTRIBUTE[i] + fields[i], rounds=MAX_ROUND)
        total += qtime
        log.info('Q%d[%s]: %f' % (i+1, ATTRIBUTE_NAME[i], qtime))
        output_json['point_query'][ATTRIBUTE_NAME[i]] = qtime

    qtime = elapsed / (MAX_ROUND * NUM_NODE)
    total += qtime
    log.info('Average Query Time: %f' %
             (total / TESTCASE_CONFIG['pointQuery']))


def rangeQueryTest():
    log.info("Range Query Test:")
    # get timestamp
    start = testcases['rangeQuery'][0].split(" ")[0]
    log.debug(testcases['rangeQuery'])
    log.debug(start)
    total = 0
    for scale in RANGE_SCALE:
        qtime = getAverageNodeRound(
            baseline.rangeQuery, int(start), int(start) + scale, rounds=MAX_ROUND)
        total += qtime
        log.info('Range %d: %f' % (scale, qtime))
        output_json['range_query'][scale] = qtime


def andQueryTest():
    log.info("And Query Test:")
    fields = testcases['andQuery'][0].split(" ")
    for r in range(2, len(AND_FIELDS)+1):
        total_qtime = 0
        count = 0
        for attr_index_list in combinations(range(len(AND_FIELDS)), r):
            attributes = []
            for attr in attr_index_list:
                attributes.append(ATTRIBUTE[attr] + fields[attr])
            qtime = getAverageNodeRound(
                baseline.andQuery, attributes, rounds=1)
            log.debug("%s(%d): %f" % ([AND_FIELDS[i]
                                       for i in attr_index_list], r, qtime))
            total_qtime += qtime
            count += 1
        log.info("%d And Query: %f" % (r, total_qtime/count))
        output_json['and_query'][r] = total_qtime/count


def storageTest():
    log.info("Storage Usage:")
    api = nodes[0]
    num_blocks = api.getinfo()["result"]["blocks"]
    size = 0
    for block in api.listblocks(str(-num_blocks), True)["result"]:
        if block["txcount"] > 1:
            size += block["size"]
    log.info(size)
    output_json['storage'] = size


def save2Json(file='benchmark.json'):
    with open(file, 'w') as f:
        json.dump(output_json, f)
