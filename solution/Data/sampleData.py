import sys
# sys.path.append('../v0.6')
# from util import Database
from pathlib import Path
import re
from random import sample


NUM_NODE = 4

SAMPLE_SIZE = 100
INPUT = 'training'
OUTPUT = 'test'
OUTPUT_DIR = str(SAMPLE_SIZE)
if not Path.exists(Path(OUTPUT_DIR)):
    Path(OUTPUT_DIR).mkdir()
# database = Database()

# database.buildFromFiles([Path('.').joinpath(
#     FILE+str(i+1)+'.txt') for i in range(NUM_NODE)])


files = [Path('.').joinpath(INPUT+str(i+1)+'.txt') for i in range(NUM_NODE)]

# print(files)


for i, f in enumerate(files):
    # sample = []
    with open(f) as lines:
        data = [line.rstrip() for line in lines]
        data = sorted(sample(data, SAMPLE_SIZE), key=lambda x: x.split('\t')[0])
        # print(*data, sep='\n')
    with open(Path(OUTPUT_DIR).joinpath(OUTPUT+str(i)+'.txt'), 'w') as output:
        output.write('\n'.join(data))
