from config import *
from util import *
from sortedcontainers import SortedKeyList
import argparse
from decoder.decoder import decoder

def full2short(full):
    if full == "Range" or full[0] == PREFIX:
        return full
    return FULL2SHORT[full]
    
def getTXids(api, stream, key):
    result = api.liststreamkeyitems(stream, key, False, MAX_RESULT)["result"]
    return [r["txid"] for r in result]

def pointQuery(api, stream, key, sort=False):
    txids = getTXids(api, full2short(stream), key)
    args = [[txid] for txid in txids]
    if stream[0] == PREFIX:
        stream = 'Timestamp'
    if sort:
        result = SortedKeyList(key=lambda x:x.split(DELIMITER)[ATTRIBUTE_INDEX[stream]])
        for r in api.batch('getrawtransaction', args):
            result.add(decoder(r["result"]))
        return result
    else:
        return [decoder(r["result"])
              for r in api.batch('getrawtransaction', args)]
    

def rangeQuery(api, start, end):
    result = []
    for i in reversed(range(NLEVEL)):
        cStep = SCALE * STEP ** i
        if start // cStep + 1 < end // cStep:
            keys = api.liststreamkeys(tsName(cStep), list(range(
                start // cStep + 1, end // cStep)))["result"]
            keys = [key['key']
                    for key in filter(lambda x:x["items"] > 0, keys)]
            for ts in keys:
                result += pointQuery(api, tsName(cStep), str(ts))
            if result:
                break
    
    data = pointQuery(api, tsName(cStep), str(start // cStep),True)
    if data:
        result += list(data.irange_key(str(start), str(end)))
    if start // cStep == end // cStep:
        return result
    data = pointQuery(api, tsName(cStep), str(end // cStep),True)
    if data:
        result += list(data.irange_key(str(start), str(end)))
    return result


def query(api, args, sort=None, order='asc'):
    streams = api.liststreams(ATTRIBUTE)["result"]
    priority = {stream['name']:stream["items"]//stream['keys'] for stream in streams}
    if "Range" in args:
        priority["Range"] = (args["Range"][1] - args["Range"][0]) // 100 # magic number
    queries = sorted(args.items(), key=lambda kv: priority[full2short(kv[0])])
    # print(queries,priority["Range"], priority["User"])
    att, val = queries[0]
    if att == 'Range':
        result = rangeQuery(api, val[0], val[1])
    else:
        result = pointQuery(api, att, val)

    for att, val in queries[1:]:
        if result == []:
            break
        if att == 'Range':
            result = list(filter(lambda x: val[0] <= int(x.split(
                DELIMITER)[0]) <= val[1], result))
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
    args = vars(parser.parse_args())
    tsRange = (args.pop('start', TIME_MIN), args.pop('end', TIME_MAX))
    if tsRange != (TIME_MIN, TIME_MAX):
        args['Range'] = tsRange
    filters = args.copy()
    del filters['sort']
    del filters['order']
    if len(filters) == 0:
        parser.error('Need at least one argument.')
    api = getAPI(auth)
    result = query(api, filters, args['sort'], args['order'])
    print(*result, sep='\n')


if __name__ == "__main__":
    main()
