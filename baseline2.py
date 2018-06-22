# hash pointer implematation

from config import ATTRIBUTE, FILE_SIZE
from util import getData, createStream
from hashlib import sha1 as hash

DATA = 'data'
INDEX = 'index'

STREAMS = [DATA, INDEX]


def createStreams(api):
    for s in STREAMS:
        createStream(api, s)


def insert(api, data):
    for line in data:
        hexstr = line.encode('utf-8').hex()
        pointer = hash(bytearray(line, encoding='utf-8')).hexdigest()
        # pointer = pointer.encode('utf-8').hex()
        api.publish(DATA, pointer, hexstr)
    # for line in data:
        # hexstr = line.encode('utf-8').hex()
        attributes = line.split(" ")
        for i in range(len(ATTRIBUTE)):
            api.publish(INDEX, ATTRIBUTE[i] + attributes[i], pointer)


def singleQuery(api, attribute, display=False):
    pointers = api.liststreamkeyitems(
        INDEX, attribute, False, FILE_SIZE)
    pointers = getData(pointers["result"], True)
    result = []
    for p in pointers:
        result += getData(api.liststreamkeyitems(DATA,
                                                 p, False, FILE_SIZE)["result"])
    # validate(result, truth[attribute])
    # result = api.liststreamkeyitems(DATA, attribute)
    if display:
        display(result)
    return result


def rangeQuery(api, start, end, display=False):
    result = []
    for timestamp in range(start, end+1):
        result += singleQuery(api, ATTRIBUTE[0]+str(timestamp), display)
    return result


def andQuery(api, attributes, display=False):
    resultSet = []
    for attr in attributes:
        # print(getData(singleQuery(api, attr)))
        resultSet.append(set(singleQuery(api, attr)))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    if display:
        display(result)
