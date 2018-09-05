from Savoir import Savoir
from config import ENCODE_FORMAT


def getAPI(auth):
    api = Savoir(auth["rpcuser"], auth["rpcpasswd"],
                 auth["rpchost"], auth["rpcport"], auth["chainname"])
    return api


def getData(result, isHex=False):
    data = []
    if result is None:
        return []
    for item in result:
        if isHex:
            data.append(item['data'])
        else:
            data.append(bytes.fromhex(item['data']).decode(ENCODE_FORMAT))
    return data
