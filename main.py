import benchmark
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


def main():
    if len(sys.argv) > 1:
        baseline = sys.argv[1]
    else:
        baseline = "baseline1"

    benchmark.loadBaseline(baseline)
    benchmark.init()
    benchmark.loadTestCases()
    benchmark.insertionTest()
    print("\n")
    benchmark.pointQueryTest()
    print("\n")
    benchmark.rangeQueryTest()
    print("\n")
    benchmark.andQueryTest()
    print("\n")
    benchmark.storageTest()
    benchmark.save2Json(baseline+'.json')


if __name__ == "__main__":
    main()
