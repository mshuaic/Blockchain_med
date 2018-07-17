from Savoir import Savoir
from timeit import default_timer as timer
from config import NUM_NODE, ATTRIBUTE_INDEX, ATTRIBUTE_NAME, ATTRIBUTE
import re

ENCODE_FORMAT = 'utf-8'


def getAPI(config, num_node):
    api = [None] * num_node
    for i in range(NUM_NODE):
        api[i] = Savoir(config["rpcuser"], config["rpcpasswd"],
                        config["rpchost"], str(config["rpcport"]+i), config["chainname"])
    # print(api[i].getinfo())
    return api


def createStream(masternode, streamPrefix):
    # streams = masternode.liststreams()['result']
    # if streamPrefix not in [item["name"] for item in streams]:
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


# def validate(lines, attributes, verbose=False):
#     for line in lines:
#         for att in attributes:
#             if att not in line.split(" "):
#                 if verbose:
#                     print("attribute: %s, %s" % (att, line))
#                     input()
#                 return False
#     return True


class Database:
    __DB = []
    __table = {}

    def buildFromFiles(self, files):
        for f in files:
            self.__DB += [re.sub('\s+', ' ', line)
                          for line in open(f)]
        self.__db2Table(ATTRIBUTE_NAME)

    def __len__(self):
        return len(self.__DB)

    def __getitem__(self, index):
        return self.__DB[index]

    def isExist(self, values):
        if isinstance(values, list):
            for v in values:
                if v not in self.__DB:
                    return False
        else:
            return values in self.__DB
        return True

    def validate(self, lines, attribute, verbose=False):
        att_dict = {short: full for short,
                    full in zip(ATTRIBUTE, ATTRIBUTE_NAME)}
        if set(self.__table[att_dict[attribute[0]]][attribute[1:]]) != set(lines):
            if verbose:
                print("attribute: %s" % attribute)
                print("lines: \n", *lines, sep='\n')
                print(
                    "truth: \n", *self.__table[att_dict[attribute[0]]][attribute[1:]], sep='\n')
                input()
            return False
        return True

    def __db2Table(self, attributes):
        for att in attributes:
            self.__table[att] = {}
            for data in self.__DB:
                values = data.split(" ")
                self.__table[att].setdefault(
                    values[ATTRIBUTE_INDEX[att]], []).append(data)


database = Database()
