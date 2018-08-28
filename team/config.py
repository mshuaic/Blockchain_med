from pathlib import Path
import json
import sys

NUM_NODE = 4

auth = None
with open('auth.json') as f:
    auth = json.load(f)

ATTRIBUTE = ['T', 'N', 'I', 'r', 'U', 'A', 'R']
ATTRIBUTE_NAME = ['Timestamp', 'Node', 'ID',
                  'Ref-ID', 'User', 'Activity', 'Resource']

ATTRIBUTE_INDEX = {'Timestamp': 0, 'Node': 1, 'ID': 2,
                   'Ref-ID': 3, 'User': 4, 'Activity': 5, 'Resource': 6}


# MAX_RESULT = NUM_NODE * FILE_SIZE
MAX_RESULT = sys.maxsize

ENCODE_FORMAT = 'ascii'

NLEVEL = 1
SCALE = 10000
STEP = 100
PREFIX = 'ts'

DATA = 'Node'
