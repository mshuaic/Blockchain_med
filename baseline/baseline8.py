# baseline8
# Add and + range Query
# Change and query algorithms
# Now and query queries one stream, then sort the result in memory
# Priority: the smaller result set has higher priority

from config import ATTRIBUTE_NAME, MAX_RESULT, ATTRIBUTE_INDEX, FILE_SIZE
from util import getData, createStream, ENCODE_FORMAT, database
from sortedcontainers import SortedList
from tqdm import tqdm


DO_VALIDATION = True

NLEVEL = 1
SCALE = 10000
STEP = 100
PREFIX = 'ts'

DATA = 'Node'


BATCH_SIZE = 1000
MAXTS = 1e12


def createStreams(api):
    for att in ATTRIBUTE_NAME[1:]:
        createStream(api, att)
    level = NLEVEL - 1
    for _ in range(NLEVEL):
        cStep = SCALE * STEP ** level
        createStream(api, PREFIX + str(cStep))
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
        attributes = ATTRIBUTE_NAME[2:]
        attributes.remove("Activity")
        # short = attributes.copy()
        # short.remove('User')
        # short.remove('Resource')
        data.append(
            {"for": "Node", "key": values[ATTRIBUTE_INDEX["Node"]], "data": hexstr})
        data.append(
            {"for": "Activity", "key": values[ATTRIBUTE_INDEX["Activity"]], "data": hexstr})
        for att in attributes:
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
        vout = 0

# def insert(api, lines):
#     result = api.listunspent(0)
#     vout = 1
#     address = api.getaddresses()["result"][0]
#     count = 0
#     args = []
#     txids = []
#     UTXOs = api.batch("preparelockunspent", [[0]] * BATCH_SIZE)
#     for utxo in UTXOs:
#         if utxo["result"] is None:
#             print(utxo)
#             input()
#         elif len(utxo["result"]["txid"]) != 64:
#             print(utxo["result"])
#             input()
#         txids.append(utxo["result"]["txid"])
#     for line in tqdm(lines):
#         hexstr = line.encode(ENCODE_FORMAT).hex()
#         values = line.split(" ")
#         data = []
#         attributes = ATTRIBUTE_NAME[2:]
#         attributes.remove("Activity")
#         data.append(
#             {"for": "Node", "key": values[ATTRIBUTE_INDEX["Node"]], "data": hexstr})
#         data.append(
#             {"for": "Activity", "key": values[ATTRIBUTE_INDEX["Activity"]], "data": hexstr})
#         for att in attributes:
#             data.append({"for": att, "key": values[ATTRIBUTE_INDEX[att]]})

#         # insert timestamp
#         level = NLEVEL - 1
#         for i in range(NLEVEL):
#             cStep = SCALE * STEP ** level
#             key = int(values[0]) // cStep
#             data.append({"for": PREFIX+str(cStep),
#                          "key": str(key)})
#             level -= 1
#         args.append([[{'txid': txids[count], 'vout': vout}],
#                      {address: 0}, data, 'send'])
#         count += 1
#         if count == BATCH_SIZE:
#             count = 0
#             txids = []
#             # UTXOs = api.batch("createrawtransaction", args)
#             api.batch("createrawtransaction", args)
#             UTXOs = api.batch("preparelockunspent", [[0]] * BATCH_SIZE)
#             for i, utxo in enumerate(UTXOs):
#                 if utxo["result"] is None:
#                     print(utxo)
#                     print(args[i])
#                     input()
#                 txids.append(utxo["result"]["txid"])
#                 # txids.append(utxo["result"])
#             args = []
#     if len(args) > 0:
#         api.batch("createrawtransaction", args)
#         count = 0
#         args = []


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
    # print(result)
    # input()
    # if stream == 'ts1':
    #     stream = "Timestamp"
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

    # ts = []
    # for v in database["Timestamp"].values():
    #     ts += v
    # # print(len(ts))
    # sl = SortedList(ts, key=lambda a: int(a.split(" ")[0]))
    # ans = list(sl.irange(str(start), str(end)))
    # print(*result, sep="\n")
    # print(*ans, sep="\n")
    # if set(result) != set(ans):
    #     # print('result:\n', *result, sep='\n')
    #     # print('ans:\n', *ans, sep='\n')
    #     print(start, end)
    #     print('result:', *(set(result) - set(ans)), sep='\n')
    #     print('ans:', *(set(ans) - set(result)), sep='\n')
    #     for a in ans:
    #         if a.split(" ")[1] == '4':
    #             print(a)
    #     # print("result:", *result, sep="\n")
    #     # print("ans:", *ans, sep="\n")
    #     input()
    return result


def andQuery(api, attAndVal):
    priority = ["Timestamp", "ID", "Ref-ID",
                "User", "Resource", "Activity", "Node"]
    for p in priority:
        temp = list(filter(lambda x: x[0] == p, attAndVal))
        if temp != []:
            break
    stream, key = temp[0]
    # stream, key = attAndVal[0]
    # print(stream, key)
    result = pointQuery(api, stream, key)
    for att, val in attAndVal:
        if result == []:
            break
        result = list(filter(lambda x: x.split(
            " ")[ATTRIBUTE_INDEX[att]] == val, result))
    # if True:
    #     temp = []
    #     # print(database[attr])
    #     for attr, value in attAndVal:
    #         temp.append(set(database[attr][value]))
    #     ans = temp[0]
    #     for i in range(1, len(temp)):
    #         ans &= temp[i]
    #     if set(ans) != set(result):
    #         print(stream, key)
    #         # print(_unidiff_output(list(ans)[0], list(result)[0]))
    #         print('attAndVal', *attAndVal, sep='\n')
    #         print('ans:', *ans, sep='\n')
    #         # print(result)
    #         print('result:', *result, sep='\n')
    #         input()
    return result


def andRangeQuery(api, start, end, attAndVal):
    result = rangeQuery(api, start, end)
    for att, val in attAndVal:
        if result == []:
            break
        # for r in result:
        # result ATTRIBUTE_INDEX
        result = list(filter(lambda x: x.split(
            " ")[ATTRIBUTE_INDEX[att]] == val, result))
    # print(result)
    # Validation
    # ts = []
    # for v in database["Timestamp"].values():
    #     ts += v
    # # print(len(ts))
    # sl = SortedList(ts, key=lambda a: int(a.split(" ")[0]))
    # ans = set(sl.irange(str(start), str(end)))

    # temp = []
    # # print(database[attr])
    # for attr, value in attAndVal:
    #     temp.append(set(database[attr][value]))
    # # ans = temp[0]
    # for i in range(len(temp)):
    #     ans &= temp[i]
    # if set(ans) != set(result):
    #     # print(_unidiff_output(list(ans)[0], list(result)[0]))
    #     print('attAndVal', *attAndVal, sep='\n')
    #     print(start, end)
    #     print('ans:', *ans, sep='\n')
    #     # print(result)
    #     print('result:', *result, sep='\n')
    #     input()

    return result

    # txids = []
    # for i in reversed(range(NLEVEL)):
    #     cStep = SCALE * STEP ** i
    #     # print(cStep)
    #     if start // cStep + 1 < end // cStep:
    #         for ts in range(start // cStep + 1, end // cStep):
    #             # result += pointQuery(api, PREFIX+str(cStep), str(ts))
    #             txids += getTXids(api, PREFIX+str(cStep), str(ts))
    #         break
    # cStep = SCALE*STEP**(NLEVEL-1)
    # # txids += getTXids(api, PREFIX+str(cStep), str(start // cStep))
    # # txids += getTXids(api, PREFIX+str(cStep), str(end // cStep))

    # args = [[DATA, txid] for txid in txids]
    # results = api.batch('getstreamitem', args)
    # result = []
    # for r in results:
    #     # print(r["result"])
    #     data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
    #     result.append(data)
    # print(*result, sep='\n')

    # keySet = [set(txids)]
    # for stream, key in attAndVal:
    #     txids = getTXids(api, stream, key)
    #     keySet.append(set(txids))
    #     # print(keySet)        # resultSet.append(set(pointQuery(api, attr, value)))
    # key = keySet[0]
    # for i in range(1, len(keySet)):
    #     key &= keySet[i]
    # # print(key)
    # result = []
    # args = [[DATA, k] for k in key]
    # results = api.batch('getstreamitem', args)
    # for r in results:
    #     data = bytes.fromhex(r["result"]["data"]).decode(ENCODE_FORMAT)
    #     result.append(data)
