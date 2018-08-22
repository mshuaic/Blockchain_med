import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import json
import sys
import os
import numpy as np

results = ['baseline1', 'baseline2']
benchmark = []
markers = ['^', 's', 'o', '*', '8', 'D']
titles = ['point_query', 'range_query', 'and_query']
xlabels = ['', 'range', 'number of and']
xrotaions = [25, 0, 0]
ROWs = 2
COLs = 3
SCALE = 0.01

plt.rcParams["figure.figsize"] = [12, 7]
plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1,
                    top=0.95, wspace=0.3, hspace=0.3)
colors = []


def addBar(bar, pos, textFormat='%.2f', yFormat=None, yLabel=None):
    ax = plt.subplot(ROWs, COLs, pos)
    rects = ax.bar(results, height=[b[bar] for b in benchmark], color=colors)
    for rect in rects:
        xloc = rect.get_x() + rect.get_width()/2
        yloc = rect.get_y() + rect.get_height()
        ax.text(xloc, yloc*0.95, textFormat %
                rect.get_height(), horizontalalignment='center')
    if yFormat is not None:
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter(yFormat))
    plt.ylabel(yLabel)
    plt.title(bar)
    if len(results) >= 3:
        plt.xticks(rotation=15)


def main():
    if len(sys.argv) > 1:
        if len(sys.argv) - 1 > len(markers):
            print("Too many files")
            exit
        global results
        results = [os.path.splitext(arg)[0] for arg in sys.argv[1:]]
        # print(results)
    for result in results:
        with open(result+'.json', 'r') as f:
            benchmark.append(json.load(f))
    ymin = sys.maxsize
    ymax = 0
    for i in range(len(titles)):
        ax = plt.subplot(ROWs, COLs, i+1)
        for j, b in enumerate(benchmark):
            p = plt.plot(b[titles[i]].keys(),
                         b[titles[i]].values(), marker=markers[j])
            colors.append(p[0].get_color())
            ymin = min(ymin, min(b[titles[i]].values()))
            ymax = max(ymax, max(b[titles[i]].values()))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        plt.yticks(np.arange(ymin, ymax+SCALE, SCALE))
        plt.xticks(rotation=xrotaions[i])
        plt.title(titles[i])
        plt.ylabel('time(s)')
        plt.xlabel(xlabels[i])
    plt.legend(results, loc='upper center', bbox_to_anchor=(0.5, -0.5))

    addBar('insertion', 4, yLabel='time(s)')
    addBar('storage', 5, '%d', '%0.0e', 'storage size(byte)')

    plt.show()


if __name__ == "__main__":
    main()
