from config import ATTRIBUTE, ATTRIBUTE_NAME, MAX_RESULT
from util import getData, createStream, ENCODE_FORMAT, database
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


def pointQuery(api, attribute, sort=False, reverse=False):
    result = api.liststreamkeyitems(
        att_dict[attribute[0]], attribute[1:], False, MAX_RESULT)
    if DO_VALIDATION:
        if database.validate(getData(result["result"]), attribute, True) == False:
            print("Wrong!")
    return getData(result["result"])


def rangeQuery(api, start, end):
    result = []
    stream = att_dict['T']
    timestamps = api.liststreamkeys(stream)["result"]
    sl = SortedList(list(map(int, [key['key'] for key in timestamps])))
    for timestamp in sl.irange(start, end):
        result += getData(api.liststreamkeyitems(stream,
                                                 str(timestamp))['result'])
    return result


def andQuery(api, attributes):
    resultSet = []
    for attr in attributes:
        resultSet.append(set(pointQuery(api, attr)))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    return list(result)


def sortResult(results, attribute, reverse=False):
    return results.sort(reverse=reverse, key=lambda line: int(line.split(" ")[att_name_index[attribute]]))
