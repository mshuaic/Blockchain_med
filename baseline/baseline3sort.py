from config import ATTRIBUTE, ATTRIBUTE_NAME, FILE_SIZE, NUM_NODE, ATTRIBUTE_TYPE
from util import getData, createStream, validate, ENCODE_FORMAT
from sortedcontainers import SortedList


DO_VALIDATION = False

att_dict = {key: value for key, value in zip(ATTRIBUTE, ATTRIBUTE_NAME)}
att_name_index = {value: counter for counter,
                  value in enumerate(ATTRIBUTE_NAME)}


def createStreams(api):
    for att in ATTRIBUTE_NAME:
        createStream(api, att)


def insert(api, data):
    result = api.listunspent(0)
    txid = result["result"][0]["txid"]
    vout = result["result"][0]["vout"]
    address = api.getaddresses()["result"][0]
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        values = line.split(" ")
        data = []
        for att, v in zip(ATTRIBUTE_NAME, values):
            data.append({"for": att, "key": v, "data": hexstr})
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        vout = 0


def pointQuery(api, attribute, sort=True, reverse=False):
    result = api.liststreamkeyitems(
        att_dict[attribute[0]], attribute[1:], False, FILE_SIZE)
    if DO_VALIDATION:
        validate(getData(result["result"]), attribute[1:])
    result = getData(result["result"])
    att_name = att_dict[attribute[0]]
    if type(ATTRIBUTE_TYPE[att_name]) is int and sort:
        result = sortResult(result, att_name, reverse)
    # print(*result, sep='\n')
    # input()
    return result


def rangeQuery(api, start, end, reverse=False):
    result = []
    stream = att_dict['T']
    timestamps = api.liststreamkeys(stream)["result"]
    sl = SortedList(list(map(int, [key['key'] for key in timestamps])))
    for timestamp in sl.irange(start, end):
        result += getData(api.liststreamkeyitems(stream,
                                                 str(timestamp))['result'])
    result = sortResult(result, stream, reverse)
    return result


def andQuery(api, attributes):
    resultSet = []
    for attr in attributes:
        resultSet.append(set(pointQuery(api, attr, sort=False)))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    return list(result)


def sortResult(results, attribute, reverse=False):
    return results.sort(reverse=reverse, key=lambda line: int(line.split(" ")[att_name_index[attribute]]))
