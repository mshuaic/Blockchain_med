from Savoir import Savoir
from config import *
from math import log10


def getAPI(auth):
    api = Savoir(auth["rpcuser"], auth["rpcpasswd"],
                 auth["rpchost"], auth["rpcport"], auth["chainname"])
    return api


def tsName(cStep):
    return PREFIX + str(int(log10(cStep)))
