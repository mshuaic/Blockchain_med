from Savoir import Savoir
from config import DELIMITER


def getAPI(auth):
    api = Savoir(auth["rpcuser"], auth["rpcpasswd"],
                 auth["rpchost"], auth["rpcport"], auth["chainname"])
    return api


def encoder(line):
    fields = line.split(DELIMITER)
    activity = fields[ATTRIBUTE_INDEX["Activity"]]
    resource = fields[ATTRIBUTE_INDEX["Resource"]]
    fields[ATTRIBUTE_INDEX["Activity"]] = activities.setdefault(
        activity, str(len(activities)))
    fields[ATTRIBUTE_INDEX["Resource"]] = resources.setdefault(
        resource, str(len(resources)))
    temp = 'f'.join(fields)
    # padding to hex string format
    if len(temp) % 2 != 0:
        temp += 'f'

        data.append(temp)


from timeit import default_timer as timer
from config import NUM_NODE, ATTRIBUTE_INDEX, ATTRIBUTE_NAME, ATTRIBUTE
import re

ENCODE_FORMAT = 'ascii'


def getAPI(config, num_node):
    api = [None] * num_node
    for i in range(NUM_NODE):
        api[i] = Savoir(config["rpcuser"], config["rpcpasswd"],
                        config["rpchost"], str(int(config["rpcport"])+i), config["chainname"])
    # print(api[i].getinfo())
    return api


def createStream(masternode, streamPrefix):
    streams = masternode.liststreams()['result']
    if streamPrefix not in [item["name"] for item in streams]:
        masternode.create('stream', streamPrefix, True)


def measure(func, *args, time=1):
    elapsed = timer()
    for i in range(time):
        func(*args)
    elapsed = timer() - elapsed
    # print("average insertion time: %f" % (elapsed / time))
    return elapsed / time


def display(result):
    for item in result:
        print(bytes.fromhex(item['data']).decode(ENCODE_FORMAT))


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


class Database:
    __DB = []
    __table = {}

    def buildFromFiles(self, files):
        for f in files:
            self.__DB += [line.rstrip() for line in open(f)]
        self.__db2Table(ATTRIBUTE_NAME)

    def __len__(self):
        return len(self.__DB)

    def __getitem__(self, index):
        if type(index) is int:
            return self.__DB[index]
        else:
            return self.__table[index]

    def isExist(self, values):
        if isinstance(values, list):
            for v in values:
                if v not in self.__DB:
                    return False
        else:
            return values in self.__DB
        return True

    def validate(self, lines, stream, key, verbose=False):
        att_dict = {short: full for short,
                    full in zip(ATTRIBUTE, ATTRIBUTE_NAME)}
        if set(self.__table[stream][key]) != set(lines):
            if verbose:
                print("attribute: %s %s" % (stream, key))
                print("lines: \n", *map(repr, lines), sep='\n')
                print(
                    "truth: \n", *map(repr, self.__table[stream][key]), sep='\n')
                input()
            return False
        return True

    def __db2Table(self, attributes):
        for att in attributes:
            self.__table[att] = {}
            for data in self.__DB:
                values = data.split(DELIMITER)
                self.__table[att].setdefault(
                    values[ATTRIBUTE_INDEX[att]], []).append(data)


database = Database()
