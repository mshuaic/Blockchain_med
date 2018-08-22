# 07/21/2018
# swtich to new benchmark suite

import benchmark2 as benchmark
import sys
import logging
# from memory_profiler import profile
from time import sleep
logging.basicConfig(level=logging.INFO, format='%(message)s')
# print(result)


# @profile
def main():
    if len(sys.argv) > 1:
        baseline = sys.argv[1]
    else:
        baseline = "baseline1"

    benchmark.loadBaseline(baseline)
    benchmark.init()
    benchmark.loadTestCases()
    benchmark.insertionTest()
    sleep(2)
    print("\n")
    benchmark.pointQueryTest()
    print("\n")
    benchmark.rangeQueryTest()
    print("\n")
    benchmark.andQueryTest()
    print("\n")
    benchmark.storageTest()
    benchmark.save2Json(baseline + '.json')
    # benchmark.save2Json(str(FILE_SIZE)+'.json')


if __name__ == "__main__":
    main()
