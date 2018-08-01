from config import ATTRIBUTE, ATTRIBUTE_NAME, MAX_RESULT
from util import getData, createStream, ENCODE_FORMAT
from sortedcontainers import SortedList


DO_VALIDATION = False

att_dict = {key: value for key, value in zip(ATTRIBUTE, ATTRIBUTE_NAME)}
att_name_index = {value: counter for counter,
                  value in enumerate(ATTRIBUTE_NAME)}
DATA = 'data'


def createStreams(api):
    for att in ATTRIBUTE_NAME:
        createStream(api, att)
    createStream(api, DATA)


def insert(api, data):
    result = api.listunspent(0)
    txid = result["result"][0]["txid"]
    vout = result["result"][0]["vout"]
    address = api.getaddresses()["result"][0]
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        values = line.split(" ")
        # unique ID = node# + user id
        uid = values[1] + values[2]
        uid = uid.encode(ENCODE_FORMAT).hex()
        data = []
        data.append({"for": DATA, "key": uid, "data": hexstr})
        for att, v in zip(ATTRIBUTE_NAME, values):
            data.append({"for": att, "key": v, "data": uid})
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        vout = 0


def getPointers(api, attribute):
    pointers = api.liststreamkeyitems(
        att_dict[attribute[0]], attribute[1:], False, MAX_RESULT)
    pointers = getData(pointers["result"], True)
    return pointers


def getValue(api, pointer):
    return getData(api.liststreamkeyitems(DATA, pointer, False, MAX_RESULT)["result"])


def pointQuery(api, attribute, sort=False, reverse=False):
    pointers = getPointers(api, attribute)
    result = []
    # api.batch(api.liststreamkeyitems, [
    # (DATA, p, False, MAX_RESULT) for p in pointers])
    for p in pointers:
        result += getValue(api, p)
    return result


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
    return result


def sortResult(results, attribute, reverse=False):
    return results.sort(reverse=reverse, key=lambda line: int(line.split(" ")[att_name_index[attribute]]))
