# hash pointer implematation

from config import ATTRIBUTE, FILE_SIZE
from util import getData, createStream, ENCODE_FORMAT


DATA = 'data'
INDEX = 'index'

DO_VALIDATION = False

STREAMS = [DATA, INDEX]


def createStreams(api):
    for s in STREAMS:
        createStream(api, s)


def insert(api, data):
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        # get unique ID (Node + ID)
        fields = line.split(" ")
        pointer = 'N' + fields[1] + fields[2]
        # hex it
        pointer = pointer.encode(ENCODE_FORMAT).hex()
        api.publish(DATA, pointer, hexstr)
        attributes = line.split(" ")
        for i in range(len(ATTRIBUTE)):
            api.publish(INDEX, ATTRIBUTE[i] + attributes[i], pointer)


def getPointers(api, attribute):
    pointers = api.liststreamkeyitems(INDEX, attribute, False, FILE_SIZE)
    pointers = getData(pointers["result"], True)
    return pointers


def getValue(api, pointer):
    return api.liststreamkeyitems(DATA, pointer, False, FILE_SIZE)["result"]


def pointQuery(api, attribute, display=False):
    pointers = getPointers(api, attribute)
    result = []
    for p in pointers:
        result += getValue(api, p)
    if DO_VALIDATION:
        result = validate(result, attribute[1:])
    if display:
        display(result)
    return result


def rangeQuery(api, start, end, display=False):
    result = []
    pointers = []
    for timestamp in range(start, end+1):
        pointers += getPointers(api, str(timestamp))
    for p in pointers:
        result += getValue(api, p)
    if display:
        display(result["result"])
    return result


# 1. get the hash pointers of an attribute A
# 2. get the hash pointers of an attribute B
# 3. intersect result 1 and 2
# 4. use the result of 3 to query data
def andQuery(api, attributes, display=False):
    keySet = []
    for attr in attributes:
        keySet.append(set(getPointers(api, attr)))
        # print(getData(pointQuery(api, attr)))
        # resultSet.append(set(getData(pointQuery(api, attr))))
    key = keySet[0]
    for i in range(1, len(keySet)):
        key &= keySet[i]
    result = []
    for k in key:
        result.append(getValue(api, k))
    if display:
        display(result)
