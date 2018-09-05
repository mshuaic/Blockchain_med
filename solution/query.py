from config import *
from util import getAPI, getData
from sortedcontainers import SortedList
# from bisect import bisect_left as left, bisect_right as right
from pathlib import Path
import argparse
from decoder.decoder import decoder


def getTXids(api, stream, key):
    result = api.liststreamkeyitems(stream, key, False, MAX_RESULT)["result"]
    return [r["txid"] for r in result]


def pointQuery(api, stream, key):
    txids = getTXids(api, stream, key)
    args = [[txid] for txid in txids]
    result = [decoder(r["result"])
              for r in api.batch('getrawtransaction', args)]
    return result


def rangeQuery(api, start, end):
    result = []
    for i in reversed(range(NLEVEL)):
        cStep = SCALE * STEP ** i
        if start // cStep + 1 < end // cStep:
            for ts in range(start // cStep + 1, end // cStep):
                result += pointQuery(api, PREFIX+str(cStep), str(ts))
            break
    cStep = SCALE*STEP**(NLEVEL-1)
    # data = pointQuery(api, PREFIX+str(cStep), str(start // cStep))
    # if data:
    #     data.sort(key=lambda a: a.split(DELIMITER)[0])
    #     result += data[left(data, str(start)): right(data, str(end))]
    # data = pointQuery(api, PREFIX+str(cStep), str(end // cStep))
    # if data:
    #     data.sort(key=lambda a: a.split(DELIMITER)[0])
    #     result += data[left(data, str(start)): right(data, str(end))]

    data = pointQuery(api, PREFIX+str(cStep), str(start // cStep))
    if data:
        sl = SortedList(data, key=lambda a: a.split(DELIMITER)[0])
        result += list(sl.irange(str(start), str(end)))
    data = pointQuery(api, PREFIX+str(cStep), str(end // cStep))
    if data:
        sl = SortedList(data, key=lambda a: a.split(DELIMITER)[0])
        result += list(sl.irange(str(start), str(end)))
    return result


def andQuery(api, attAndVal):
    priority = ["ID", "Ref-ID", "Range"
                "User", "Resource", "Activity", "Node"]
    priority = dict(zip(priority, range(len(priority))))
    for p in priority:
        temp = list(filter(lambda x: x[0] == p, attAndVal))
        if temp != []:
            break
    stream, key = temp[0]
    result = pointQuery(api, stream, key)
    for att, val in attAndVal:
        if result == []:
            break
        result = list(filter(lambda x: x.split(
            DELIMITER)[ATTRIBUTE_INDEX[att]] == val, result))
    return result


def query(api, args, sort=None, order='asc'):
    priority = ["ID", "Ref-ID", "Range",
                "User", "Resource", "Activity", "Node"]
    priority = dict(zip(priority, range(len(priority))))
    queries = sorted(args.items(), key=lambda kv: priority[kv[0]])
    att, val = queries[0]
    if att == 'Range':
        result = rangeQuery(api, val[0], val[1])
    else:
        result = pointQuery(api, att, val)

    for att, val in queries[1:]:
        if result == []:
            break
        if att == 'Range':
            result = list(filter(lambda x: val[0] <= x.split(
                DELIMITER)[ATTRIBUTE_INDEX[att]] <= val[1], result))
        else:
            result = list(filter(lambda x: x.split(
                DELIMITER)[ATTRIBUTE_INDEX[att]] == val, result))
    if sort != None:
        result.sort(reverse=(order != 'asc'), key=lambda line: int(
            line.split(DELIMITER)[ATTRIBUTE_INDEX[sort]]))
    return result


def main():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument(
        "-st", help="Filter this query to entries >= start_time", type=int, dest='start', metavar='START_TIME')
    parser.add_argument(
        "-et", help="Filter this query to entries <= end_time", type=int, dest='end', metavar='END_TIME',)
    parser.add_argument(
        "-node", help="Filter this query by node", type=str, dest='Node')
    parser.add_argument(
        "-id", help="Filter this query by id", type=str, dest='ID')
    parser.add_argument(
        "-ref", help="Filter this query by ref_id", type=str, dest='Ref-ID')
    parser.add_argument(
        "-user", help="Filter this query by user", type=str, dest='User')
    parser.add_argument(
        "-act", help="Filter this query by activity", type=str, dest='Activity')
    parser.add_argument(
        "-res", help="Filter this query by resource", type=str, dest='Resource')
    parser.add_argument(
        "-sort", help="Sort this query by provided column", choices=list(map(str.casefold, ATTRIBUTE_NAME[:-2])), default=None)
    parser.add_argument(
        "-order", help="Sort this query in 'asc' or 'desc' order", choices=['asc', 'desc'], default='asc')
    # print(vars(parser.parse_args()))
    # input()
    # args = dict(filter(lambda kv: kv[1] != None,
    #                    vars(parser.parse_args()).items()))
    # if 'Range' in args:
    #     if not any(args['Range']):
    #         del args['Range']
    args = vars(parser.parse_args())
    tsRange = (args.pop('start', TIME_MIN), args.pop('end', TIME_MAX))
    if tsRange != (TIME_MIN, TIME_MAX):
        args['Range'] = tsRange
    filters = args.copy()
    del filters['sort']
    del filters['order']
    if len(args) == 0:
        parser.error('Need at least one argument.')
    api = getAPI(auth)
    result = query(api, filters, args['sort'], args['order'])

    print(*result, sep='\n')


if __name__ == "__main__":
    main()
