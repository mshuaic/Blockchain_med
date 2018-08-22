# Baseline 5
# Build index tree for timestamp on blockchain

from config import ATTRIBUTE, ATTRIBUTE_NAME, MAX_RESULT, ATTRIBUTE_INDEX, ATT_S2F
from util import getData, createStream, ENCODE_FORMAT, database
from sortedcontainers import SortedList, SortedKeyList
import pandas as pd

DO_VALIDATION = False


# att_dict = {key: value for key, value in zip(ATTRIBUTE, ATTRIBUTE_NAME)}
# att_name_index = {value: counter for counter,
#                   value in enumerate(ATTRIBUTE_NAME)}

# TSScale = '%Y%m%d%H%M%S'
SCALE = 10000


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
        # ts = values[0]
        # tskey = pd.to_datetime(int(ts), unit='ms').strftime(TSScale)
        # data.append({"for": 'Timestamp', "key": tskey, "data": hexstr})
        data.append(
            {"for": 'Timestamp', "key": str(int(values[0])//SCALE), "data": hexstr})
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        vout = 0


# sort the result in memory
# NEED TO TEST AGAIN
# def pointQuery(api, attribute, sort=False, reverse=False):
#     # if attribute[0] == 'T':

#     result = api.liststreamkeyitems(
#         ATT_S2F[attribute[0]], attribute[1:], False, MAX_RESULT)
#     result = getData(result["result"])
#     temp = []
#     if attribute[0] == 'U' or attribute[0] == 'R':
#         # print(result)
#         for line in result:
#             node, ID = line.split(" ")[1:3]
#             RIDResult = getData(api.liststreamkeyitems(
#                 'Ref-ID', ID, False, MAX_RESULT)["result"])
#             for r in RIDResult:
#                 if r.split(" ")[1] == node:
#                     temp += [r]
#             # print(*temp)
#     result += temp
#     if DO_VALIDATION:  # and attribute[0] != 'U' and attribute[0] != 'R':
#         if database.validate(result, attribute, True) is False:
#             print("Wrong!")
#     return result

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
    # print(start, end)
    result = []
    for ts in range(start // SCALE + 1, end // SCALE):
        # print('ts:', ts)
        # temp = api.liststreamkeyitems(TIMESTAMPE, str(ts))['result']
        temp = pointQuery(api, TIMESTAMPE, str(ts))
        # print(temp)
        if temp:
            result += temp
        # print(result)
    temp = api.liststreamkeyitems(TIMESTAMPE, str(start // SCALE))['result']
    # print('in range:\n', *result, sep='\n')
    if temp:
        data = getData(temp)
        # print(data)
        sl = SortedList(data, key=lambda a: a.split(" ")[0])
        result += list(sl.irange(str(start), str(end)))
    temp = api.liststreamkeyitems(TIMESTAMPE, str(end // SCALE))['result']
    if temp:
        data = getData(temp)
        sl = SortedList(data, key=lambda a: a.split(" ")[0])
        # print('end:')
        # print(*list(sl.irange(maximum=str(end))), sep='\n')
        result += list(sl.irange(str(start), str(end)))

    return result
    # ans = []
    # timestamps = api.liststreamkeys(TIMESTAMPE)["result"]
    # sl = SortedList(list(map(int, [key['key'] for key in timestamps])))
    # for timestamp in sl.irange(start, end):
    #     ans += getData(api.liststreamkeyitems(TIMESTAMPE,
    #                                           str(timestamp))['result'])
    # ts = [v[0] for v in database[TIMESTAMPE].values()][:400]
    # sl = SortedKeyList(ts, key=lambda a: a.split(" ")[0])
    # ans = list(sl.irange(str(start), str(end)))
    # if set(result) != set(ans):
    #     # print('result:\n', *result, sep='\n')
    #     # print('ans:\n', *ans, sep='\n')
    #     print('result:\n', *(set(result) - set(ans)), sep='\n')
    #     print('ans:\n', *(set(ans) - set(result)), sep='\n')
    #     input()
    #     input()

# 483730
# def rangeQuery(api, start, end):
#     result = []
#     stream = att_dict['T']
#     timestamps = api.liststreamkeys(stream)["result"]
#     sl = SortedList(list(map(int, [key['key'] for key in timestamps])))
#     for timestamp in sl.irange(start, end):
#         result += getData(api.liststreamkeyitems(stream,
#                                                  str(timestamp))['result'])
#         # print("length: ", len(result), result)
#         # input()
#     return result


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
