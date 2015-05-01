__author__ = 'wangzaicheng'

import codecs
import collections

with open("ValidProTag.txt") as w:
    curr_list = collections.Counter()
    for line in w.readlines():
        curr = line.strip().split('\t')
        curr_list[curr[0].lower()] += int(curr[1])

ret = sorted(curr_list.items(), key=lambda x: x[1], reverse=True)
with open("ValidProTag.txt", "wb") as w:
    for r in ret:
        w.write(r[0] + '\t' + str(r[1]) + '\n')

