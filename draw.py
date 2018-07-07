import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import json
import sys
import os

results = ['baseline1', 'baseline2']
benchmark = []
markers = ['^', 's', 'o', '*', '8', 'D']
titles = ['point_query', 'range_query', 'and_query']
xlabels = ['', 'range', 'number of and']
xrotaions = [25, 0, 0]
ROWs = 2
COLs = 3

plt.rcParams["figure.figsize"] = [12, 7]
plt.subplots_adjust(left=0.1, right=0.95, bottom=0.05,
                    top=0.95, wspace=0.3, hspace=0.3)
colors = []


def addBar(bar, pos, textFormat='%.2f', yFormat=None, yLabel=None):
    ax = plt.subplot(ROWs, COLs, pos)
    rects = ax.bar(results, height=[b[bar] for b in benchmark], color=colors)
    for rect in rects:
        width = int(rect.get_width())
        xloc = rect.get_x() + rect.get_width()/2
        yloc = rect.get_y() + rect.get_height()
        ax.text(xloc, yloc*0.95, textFormat %
                rect.get_height(), horizontalalignment='center')
    if yFormat is not None:
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter(yFormat))
    plt.ylabel(yLabel)
    plt.title(bar)


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
    for i in range(len(titles)):
        plt.subplot(ROWs, COLs, i+1)
        for j, b in enumerate(benchmark):
            p = plt.plot(b[titles[i]].keys(),
                         b[titles[i]].values(), marker=markers[j])
            colors.append(p[0].get_color())
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
