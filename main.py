import benchmark
import sys


def main():
    if len(sys.argv) > 1:
        baseline = sys.argv[1]
    else:
        baseline = "baseline1"
    benchmark.loadBaseline(baseline)
    benchmark.init()
    benchmark.insertionTest()
    print("\n")
    benchmark.singleQueryTest()
    print("\n")
    benchmark.rangeQueryTest()
    print("\n")
    benchmark.andQueryTest()
    print("\n")
    benchmark.storageTest()


if __name__ == "__main__":
    main()
