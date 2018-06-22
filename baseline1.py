from config import ATTRIBUTE, FILE_SIZE
from util import getData, createStream

STREAM = 'data'


def createStreams(api):
    createStream(api, STREAM)


def insert(api, data):
    for line in data:
        hexstr = line.encode('utf-8').hex()
        attributes = line.split(" ")
        for i in range(len(ATTRIBUTE)):
            api.publish(STREAM, ATTRIBUTE[i] + attributes[i], hexstr)


def singleQuery(api, attribute, display=False):
    result = api.liststreamkeyitems(STREAM, attribute, False, FILE_SIZE)
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
