# Most lines' ref-ID are refer back to the same original ID,
# which means those lines' User and Resource are the same. For this
# reason, we can exculde User and Resource in transaction. When node
# queries User and Resource, the baseline4 first get its original
# Node+ID, and use Node+RID to query additional result and union them

# baseline4_1
# add Node + RID stream
# this method saves data ob blockchain
# user can query the Node+RID result directly from blockchain instead
# of sorting form memory


from config import ATTRIBUTE, ATTRIBUTE_NAME, MAX_RESULT
from util import getData, createStream, ENCODE_FORMAT, database
from sortedcontainers import SortedList


DO_VALIDATION = True

att_dict = {key: value for key, value in zip(ATTRIBUTE, ATTRIBUTE_NAME)}
att_name_index = {value: counter for counter,
                  value in enumerate(ATTRIBUTE_NAME)}

# UID = 'UID'
NRID = 'NRID'


def createStreams(api):
    for att in ATTRIBUTE_NAME:
        createStream(api, att)
    # createStream(api, UID)
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
        short = ATTRIBUTE_NAME.copy()
        short.remove('User')
        short.remove('Resource')
        uid = values[1] + 'N' + values[2]
        if values[att_name_index['ID']] == values[att_name_index['Ref-ID']]:
            for att, v in zip(ATTRIBUTE_NAME, values):
                # if att == 'Timestamp' or att == 'ID':
                #     data.append(
                #         {"for": att, "key": v, "data": uid.encode(ENCODE_FORMAT).hex()})
                # else:
                data.append({"for": att, "key": v, "data": hexstr})
        else:
            for key in short:
                # if key == 'Timestamp' or key == 'ID':
                #     data.append(
                #         {"for": key, "key": values[att_name_index[key]], "data": uid.encode(ENCODE_FORMAT).hex()})
                # else:
                data.append(
                    {"for": key, "key": values[att_name_index[key]], "data": hexstr})

        nrid = values[1] + 'R' + values[3]
        # data.append({"for": UID, "key": uid, "data": hexstr})
        data.append({"for": NRID, "key": nrid, "data": hexstr})
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        vout = 0


# sort the result using RID in blockchain
def pointQuery(api, attribute, sort=False, reverse=False):
    # result = []
    result = api.liststreamkeyitems(
        att_dict[attribute[0]], attribute[1:], False, MAX_RESULT)
    result = getData(result["result"])
    temp = []
    # if attribute[0] == 'T' or attribute[0] == 'I':
    #     for uid in getData(api.liststreamkeyitems(
    #             att_dict[attribute[0]], attribute[1:], False, MAX_RESULT)["result"]):
    #         # print("Uid", uid)
    #         result += getData(api.liststreamkeyitems(UID,
    #                                                  uid, False, MAX_RESULT)["result"])
    # else:
    #     result += getData(api.liststreamkeyitems(
    #         att_dict[attribute[0]], attribute[1:], False, MAX_RESULT)["result"])

    if attribute[0] == 'U' or attribute[0] == 'R':
        for line in result:
            node, _, RID = line.split(" ")[1:4]
            nrid = node + 'R' + RID
            RIDResult = getData(api.liststreamkeyitems(
                NRID, nrid, False, MAX_RESULT)["result"])
            temp += RIDResult
    #         for r in RIDResult:
    #             if r.split(" ")[1] == node:
    #                 temp += [r]
    result += temp
    if DO_VALIDATION:  # and attribute[0] != 'U' and attribute[0] != 'R':
        if database.validate(result, attribute, True) is False:
            print("Wrong!")
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
    resultSet = []
    for attr in attributes:
        resultSet.append(set(pointQuery(api, attr)))
    result = resultSet[0]
    for i in range(1, len(resultSet)):
        result &= resultSet[i]
    return list(result)


def sortResult(results, attribute, reverse=False):
    return results.sort(reverse=reverse, key=lambda line: int(line.split(" ")[att_name_index[attribute]]))
