import json
import sys

NUM_NODE = 4

auth = None
with open('auth.json') as f:
    auth = json.load(f)

ATTRIBUTE = ['T', 'N', 'I', 'F', 'U', 'A', 'R']
ATTRIBUTE_NAME = ['Timestamp', 'Node', 'ID',
                  'Ref-ID', 'User', 'Activity', 'Resource']
FULL2SHORT = {full:short for full,short in zip(ATTRIBUTE_NAME,ATTRIBUTE)}
ATTRIBUTE_INDEX = {att: i for i, att in enumerate(ATTRIBUTE_NAME)}
ATTRIBUTE_INDEX.update(
    {att: i for i, att in enumerate(map(str.lower, ATTRIBUTE_NAME))})
ATTRIBUTE_INDEX.update({att: i for i, att in enumerate(ATTRIBUTE)})

# MAX_RESULT = NUM_NODE * FILE_SIZE
MAX_RESULT = int(1e9)

ENCODE_FORMAT = 'ascii'

NLEVEL = 3
SCALE = 10000
STEP = 100
PREFIX = 's'

TIME_MIN = 0
TIME_MAX = (2 ** 31 -1) * 1000

DELIMITER = '\t'
