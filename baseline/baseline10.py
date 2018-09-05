# baseline10
# use empty values

from config import ATTRIBUTE_NAME, MAX_RESULT, ATTRIBUTE_INDEX, FILE_SIZE, DELIMITER
from util import getData, createStream, ENCODE_FORMAT, database
from sortedcontainers import SortedList
from tqdm import tqdm
from decoder.decoder import decoder


DO_VALIDATION = True

NLEVEL = 1
SCALE = 10000
STEP = 100
PREFIX = 'ts'

DATA = 'Node'


BATCH_SIZE = 1000
MAXTS = 1e12


def createStreams(api):
    for att in ATTRIBUTE_NAME:
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
        values = line.split(DELIMITER)
        data = []
        attributes = ATTRIBUTE_NAME
        for att in attributes:
            data.append({"for": att, "key": values[ATTRIBUTE_INDEX[att]]})
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


def getTXids(api, stream, key):
    # txids = []
    result = api.liststreamkeyitems(stream, key, False, MAX_RESULT)["result"]
    txids = [r["txid"] for r in result]
    # for r in result:
    #     txids.append(r["txid"])
    return txids


def pointQuery(api, stream, key):
    txids = getTXids(api, stream, key)
    args = [[txid] for txid in txids]
    result = [decoder(r["result"])
              for r in api.batch('getrawtransaction', args)]

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
        sl = SortedList(data, key=lambda a: a.split(DELIMITER)[0])
        result += list(sl.irange(str(start), str(end)))
    data = pointQuery(api, PREFIX+str(cStep), str(end // cStep))
    if data:
        # data = getData(temp)
        sl = SortedList(data, key=lambda a: a.split(DELIMITER)[0])
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
            DELIMITER)[ATTRIBUTE_INDEX[att]] == val, result))
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
