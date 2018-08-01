# Baseline 5_1
# 2-level indexing for timestamps

# Baseline 5
# Build index tree for timestamp on blockchain

from config import ATTRIBUTE_NAME, MAX_RESULT, ATTRIBUTE_INDEX
from util import getData, createStream, ENCODE_FORMAT, database
from sortedcontainers import SortedList


DO_VALIDATION = False

NLEVEL = 2
SCALE = 10000
STEP = 100


def createStreams(api):
    for att in ATTRIBUTE_NAME:
        createStream(api, att)
    level = NLEVEL - 1
    for _ in range(NLEVEL):
        cStep = SCALE * STEP ** level
        createStream(api, "ts" + str(cStep))
        level -= 1


def __insertTS(api, data, ts, hexstr):
    key = ts
    level = NLEVEL - 1
    for i in range(NLEVEL):
        cStep = SCALE * STEP ** level
        key = ts // cStep
        data.append({"for": "Timestamp", "key": str(key), "data": hexstr})
        level -= 1


def insert(api, data):
    result = api.listunspent(0)
    txid = result["result"][0]["txid"]
    vout = result["result"][0]["vout"]
    address = api.getaddresses()["result"][0]
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        values = line.split(" ")
        data = []
        attributes = ATTRIBUTE_NAME[1:]
        short = attributes.copy()
        short.remove('User')
        short.remove('Resource')
        if values[ATTRIBUTE_INDEX['ID']] == values[ATTRIBUTE_INDEX['Ref-ID']]:
            for att in attributes:
                data.append(
                    {"for": att, "key": values[ATTRIBUTE_INDEX[att]], "data": hexstr})
        else:
            for key in short:
                data.append(
                    {"for": key, "key": values[ATTRIBUTE_INDEX[key]], "data": hexstr})

        # build indexing structure for timestamp
        # data.append(
        #     {"for": 'Timestamp', "key": str(int(values[0])//SCALE), "data": hexstr})
        # __insertTS(api, data, int(values[0], hexstr))
        level = NLEVEL - 1
        for i in range(NLEVEL):
            cStep = SCALE * STEP ** level
            key = int(values[0]) // cStep
            data.append({"for": "ts"+str(cStep),
                         "key": str(key), "data": hexstr})
            level -= 1
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        vout = 0


def pointQuery(api, attribute, value):
    if attribute == "Timestamp":
        TSResult = getData(api.liststreamkeyitems(
            'Timestamp', str(int(value) // SCALE), False, MAX_RESULT)["result"])
        for tsr in TSResult:
            ts = tsr.split(" ")[0]
            if ts == value:
                return [tsr]
    result = getData(api.liststreamkeyitems(
        attribute, value, False, MAX_RESULT)["result"])
    temp = []
    if attribute == "User" or attribute == "Resource":
        for line in result:
            node, ID = line.split(" ")[1:3]
            RIDResult = getData(api.liststreamkeyitems(
                'Ref-ID', ID, False, MAX_RESULT)["result"])
            for r in RIDResult:
                if r.split(" ")[1] == node:
                    temp += [r]
    result += temp
    return result


def rangeQuery(api, start, end):
    TIMESTAMPE = 'Timestamp'
    result = []
    for ts in range(start // SCALE + 1, end // SCALE):
        temp = pointQuery(api, TIMESTAMPE, str(ts))
        if temp:
            result += temp
    temp = api.liststreamkeyitems(TIMESTAMPE, str(start // SCALE))['result']
    if temp:
        data = getData(temp)
        sl = SortedList(data, key=lambda a: a.split(" ")[0])
        result += list(sl.irange(str(start), str(end)))
    temp = api.liststreamkeyitems(TIMESTAMPE, str(end // SCALE))['result']
    if temp:
        data = getData(temp)
        sl = SortedList(data, key=lambda a: a.split(" ")[0])
        result += list(sl.irange(str(start), str(end)))

    return result


def andQuery(api, attAndVal):
    resultSet = []
    for attr, value in attAndVal:
        resultSet.append(set(pointQuery(api, attr, value)))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    if DO_VALIDATION is True:
        temp = []
        # print(database[attr])
        for attr, value in attAndVal:
            temp.append(set(database[attr][value]))
        ans = temp[0]
        for i in range(1, len(temp)):
            ans &= temp[i]
        if ans != result:
            print('ans:', *ans, sep='\n')
            print('result:'*result, sep='\n')
    return list(result)


def sortResult(results, attribute, reverse=False):
    return results.sort(reverse=reverse, key=lambda line: int(line.split(" ")[att_name_index[attribute]]))
