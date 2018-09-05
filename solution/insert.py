from config import *
from util import getAPI
from pathlib import Path
import argparse
import re


def insert(api, data):
    result = api.listunspent(0)
    txid = result["result"][0]["txid"]
    vout = result["result"][0]["vout"]
    address = api.getaddresses()["result"][0]
    size = len(data)
    counter = 0
    for line in data:
        print("%d / %d" % (counter, size))
        counter += 1
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="pass a file path", type=Path)
    args = parser.parse_args()
    with open(args.file) as f:
        data = [line.rstrip() for line in f]
    api = getAPI(auth)
    insert(api, data)


if __name__ == "__main__":
    main()
