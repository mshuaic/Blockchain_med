from config import ATTRIBUTE, FILE_SIZE
from util import getData, createStream, validate, ENCODE_FORMAT

STREAM = 'data'
DO_VALIDATION = False


def createStreams(api):
    createStream(api, STREAM)


def insert(api, data):
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        attributes = line.split(" ")
        for i in range(len(ATTRIBUTE)):
            api.publish(STREAM, ATTRIBUTE[i] + attributes[i], hexstr)


def pointQuery(api, attribute, display=False, validation=DO_VALIDATION):
    result = api.liststreamkeyitems(STREAM, attribute, False, FILE_SIZE)
    if validation:
        validate(getData(result["result"]), attribute[1:])
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
        # print(getData(pointQuery(api, attr)))
        resultSet.append(set(getData(pointQuery(api, attr))))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    if display:
        display(result)
