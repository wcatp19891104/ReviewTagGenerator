__author__ = 'wangzaicheng'

import collections
import matplotlib
matplotlib.use('TkAgg')
import pylab
import matplotlib.pyplot as plt
from numpy import diff


def adjuster(file_name, threshold=0.9):
    record = collections.OrderedDict()
    total = 0
    for data in open(file_name).readlines():
        curr = data.strip().split('\t')
        record[curr[0]] = int(curr[1])
        total += int(curr[1])

    curr_count = 0
    curr_list = list()
    ratio_list = list()
    for item in record.items():
        curr_count += item[1]
        curr_list.append(item[0])
        ratio_list.append(curr_count / float(total))
        if curr_count / float(total) >= threshold:
            break

    x = pylab.arange(1, len(ratio_list) + 1, 1)
    plt.plot(x, ratio_list)
    plt.show()

    dx = 1
    dy = diff(ratio_list) / dx
    print len(dy)
    print len(x)
    x = pylab.arange(1, len(ratio_list), 1)
    plt.plot(x, dy)
    plt.show()

    print dy


    return curr_list


if __name__ == "__main__":
    test = adjuster('../resource/pro.txt', 0.80)
    print len(test)
    open('../resource/validate_80_pro.txt', 'wb').write('\n'.join(test))

