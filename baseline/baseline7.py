# baseline7
# baseline6 + database normalization

from config import ATTRIBUTE_NAME, MAX_RESULT, ATTRIBUTE_INDEX
from util import getData, createStream, ENCODE_FORMAT, database
from sortedcontainers import SortedList
# import difflib
from functools import reduce

DO_VALIDATION = True

NLEVEL = 1
SCALE = 10000
STEP = 100
PREFIX = 'ts'

DATA = 'Node'
NRID = 'NRID'


def createStreams(api):
    for att in ATTRIBUTE_NAME[1:]:
        createStream(api, att)
    level = NLEVEL - 1
    for _ in range(NLEVEL):
        cStep = SCALE * STEP ** level
        createStream(api, PREFIX + str(cStep))
        level -= 1
    createStream(api, NRID)


def insert(api, data):
    result = api.listunspent(0)
    txid = result["result"][0]["txid"]
    vout = result["result"][0]["vout"]
    address = api.getaddresses()["result"][0]
    for line in data:
        hexstr = line.encode(ENCODE_FORMAT).hex()
        values = line.split(" ")
        data = []
        attributes = ATTRIBUTE_NAME[2:]
        attributes.remove("Activity")
        short = attributes.copy()
        short.remove('User')
        short.remove('Resource')
        data.append(
            {"for": "Node", "key": values[ATTRIBUTE_INDEX["Node"]], "data": hexstr})
        data.append(
            {"for": "Activity", "key": values[ATTRIBUTE_INDEX["Activity"]], "data": hexstr})
        if values[ATTRIBUTE_INDEX["ID"]] == values[ATTRIBUTE_INDEX["Ref-ID"]]:
            for att in attributes:
                data.append({"for": att, "key": values[ATTRIBUTE_INDEX[att]]})
        else:
            data.append(
                {"for": NRID, "key": values[ATTRIBUTE_INDEX["Node"]]+"R"+values[ATTRIBUTE_INDEX["Ref-ID"]]})
            for att in short:
                data.append({"for": att, "key": values[ATTRIBUTE_INDEX[att]]})

        # insert timestamp
        level = NLEVEL - 1
        for i in range(NLEVEL):
            cStep = SCALE * STEP ** level
            key = int(values[0]) // cStep
            data.append({"for": PREFIX+str(cStep),
                         "key": str(key)})
            level -= 1
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        # print(txid)
        # input()
        vout = 0


def getTXids(api, stream, key):
    txids = []
    result = api.liststreamkeyitems(stream, key, False, MAX_RESULT)["result"]
    for r in result:
        txids.append(r["txid"])
    return txids


def pointQuery(api, stream, key):
    if stream == "Timestamp":
        txids = getTXids(api, PREFIX + str(SCALE),
                         str(int(key) // SCALE))
        # resulls = api.getstreamitem(DATA, txids[0])
    elif stream == DATA or stream == 'Activity':
        return getData(api.liststreamkeyitems(stream, key, False, MAX_RESULT)["result"])
    else:
        txids = getTXids(api, stream, key)
    args = [[DATA, txid] for txid in txids]
    results = api.batch('getstreamitem', args)
    result = []
    for r in results:
        # print(r["result"])
        data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
        if stream == "Timestamp":
            if data.split(" ")[0] == key:
                result = [data]
                break
                # return data
        else:
            result.append(data)
    if stream == "User" or stream == 'Resource':
        # txids = getTXids(api, stream, key)
        nrids = []
        for line in result:
            node, _, rid = line.split(" ")[1:4]
            nrids.append(node + 'R' + rid)
        args = [[NRID, nrid, False, MAX_RESULT] for nrid in nrids]
        temp = api.batch('liststreamkeyitems', args)
        # print(*temp, sep='\n')
        # input()
        ridResults = []
        for r in temp:
            ridResults += r["result"]
        txids = [tx["txid"] for tx in ridResults]
        args = [[DATA, txid] for txid in txids]
        results = api.batch('getstreamitem', args)
        temp = []
        for r in results:
            data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
            temp.append(data)
        result += temp
        # if database.validate(result, stream, key, True) is False:
        # print("Wrong!")
    return result


def rangeQuery(api, start, end):
    # print(start, end)
    result = []
    for i in reversed(range(NLEVEL)):
        cStep = SCALE * STEP ** i
        # print(cStep)
        if start // cStep + 1 < end // cStep:
            for ts in range(start // cStep + 1, end // cStep):
                result += pointQuery(api, PREFIX+str(cStep), str(ts))
                # print("hello")
                # print(result)
            break
    cStep = SCALE*STEP**(NLEVEL-1)
    data = pointQuery(api, PREFIX+str(cStep), str(start // cStep))
    if data:
        # data = getData(temp)
        sl = SortedList(data, key=lambda a: a.split(" ")[0])
        result += list(sl.irange(str(start), str(end)))
    data = pointQuery(api, PREFIX+str(cStep), str(end // cStep))
    if data:
        # data = getData(temp)
        sl = SortedList(data, key=lambda a: a.split(" ")[0])
        result += list(sl.irange(str(start), str(end)))

    return result
    # ts = [v[0] for v in database["Timestamp"].values()]
    # sl = SortedList(ts, key=lambda a: a.split(" ")[0])
    # if set(result) != set(ans):
    # ans = list(sl.irange(str(start), str(end)))
    #     # print('result:\n', *result, sep='\n')
    #     # print('ans:\n', *ans, sep='\n')
    #     print('result:\n', *(set(result) - set(ans)), sep='\n')
    #     print('ans:\n', *(set(ans) - set(result)), sep='\n')
    #     input()

    # print(result)
    # input()
    #     level -= 1
    # for ts in range(start // SCALE + 1, end // SCALE):
    #     temp = pointQuery(api, TIMESTAMPE, str(ts))
    #     if temp:
    #         result += temp
    # temp = api.liststreamkeyitems(TIMESTAMPE, str(start // SCALE))['result']
    # if temp:
    #     data = getData(temp)
    #     sl = SortedList(data, key=lambda a: a.split(" ")[0])
    #     result += list(sl.irange(str(start), str(end)))
    # temp = api.liststreamkeyitems(TIMESTAMPE, str(end // SCALE))['result']
    # if temp:
    #     data = getData(temp)
    #     sl = SortedList(data, key=lambda a: a.split(" ")[0])
    #     result += list(sl.irange(str(start), str(end)))

    # return result


def andQuery(api, attAndVal):
    keySet = []
    for stream, key in attAndVal:
        if stream == "Timestamp":
            txids = getTXids(api, PREFIX + str(SCALE),
                             str(int(key) // SCALE))
            args = [[DATA, txid] for txid in txids]
            results = api.batch('getstreamitem', args)
            for r in results:
                # print(r["result"])
                data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
                # print(data)
                if data.split(" ")[0] == key:
                    txids = [r["result"]["txid"]]
                    # print(data, attAndVal)
                    # input()
                    break
        else:
            txids = getTXids(api, stream, key)
        if stream == "User" or stream == 'Resource':
            # print(txids)
            args = [[DATA, txid] for txid in txids]
            results = api.batch('getstreamitem', args)
            result = []
            for r in results:
                data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
                result.append(data)
            # print(result)
            nrids = []
            for line in result:
                node, _, rid = line.split(" ")[1:4]
                nrids.append(node + 'R' + rid)
                args = [[NRID, nrid, False, MAX_RESULT] for nrid in nrids]
                temp = api.batch('liststreamkeyitems', args)
            ridResults = []
            for r in temp:
                ridResults += r["result"]
            txids += [tx["txid"] for tx in ridResults]
        keySet.append(set(txids))
        # print(keySet)
        # resultSet.append(set(pointQuery(api, attr, value)))
    key = keySet[0]
    for i in range(1, len(keySet)):
        key &= keySet[i]
    # print(key)
    result = []
    args = [[DATA, k] for k in key]
    results = api.batch('getstreamitem', args)
    for r in results:
        data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
        result.append(data)

    # if True:
    #     temp = []
    #     # print(database[attr])
    #     for attr, value in attAndVal:
    #         temp.append(set(database[attr][value]))
    #     ans = temp[0]
    #     for i in range(1, len(temp)):
    #         ans &= temp[i]
    #     if set(ans) != set(result):
    #         # print(_unidiff_output(list(ans)[0], list(result)[0]))
    #         print('attAndVal', *attAndVal, sep='\n')
    #         print('ans:', *ans, sep='\n')
    #         # print(result)
    #         print('result:', *result, sep='\n')
    #         print('keySet:', keySet)
    #         input()
    return result


def sortResult(results, attribute, reverse=False):
    return results.sort(reverse=reverse, key=lambda line: int(line.split(" ")[att_name_index[attribute]]))
