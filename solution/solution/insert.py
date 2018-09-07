from config import *
from util import *
import argparse
from tqdm import tqdm

def insert(api, data):
    result = api.listunspent(0)
    txid = result["result"][0]["txid"]
    vout = result["result"][0]["vout"]
    address = api.getaddresses()["result"][0]
    for line in tqdm(data):
        values = line.split(DELIMITER)
        data = []
        attributes = ATTRIBUTE
        for att in attributes:
            data.append({"for": att, "key": values[ATTRIBUTE_INDEX[att]]})
        for i in range(NLEVEL):
            cStep = SCALE * STEP ** i
            key = int(values[0]) // cStep
            data.append({"for": tsName(cStep),
                         "key": str(key)})
        txid = api.createrawtransaction(
            [{'txid': txid, 'vout': vout}], {address: 0}, data, 'send')["result"]
        vout = 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="pass a file path", type=str)
    args = parser.parse_args()
    with open(args.file) as f:
        data = [line.rstrip() for line in f]
    api = getAPI(auth)
    insert(api, data)


if __name__ == "__main__":
    main()
