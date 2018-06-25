# hash pointer implematation

from config import ATTRIBUTE, FILE_SIZE
from util import getData, createStream, validate, ENCODE_FORMAT
from hashlib import sha1 as hash
# from zlib import crc32 as hash


DATA = 'data'
INDEX = 'index'

DO_VALIDATION = True

STREAMS = [DATA, INDEX]


def createStreams(api):
    for s in STREAMS:
        createStream(api, s)


# def hash(data):
#     return 11


def insert(api, data):
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        pointer = hash(bytearray(line, encoding=ENCODE_FORMAT)).hexdigest()
        # pointer = str(hash(bytearray(line, encoding=ENCODE_FORMAT))
        # ).encode(ENCODE_FORMAT).hex()
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
    if DO_VALIDATION:
        result = validate(result, attribute[1:])

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
