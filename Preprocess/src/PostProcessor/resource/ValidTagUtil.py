# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


SAME_FILE = "similar_tag.txt"
TAG_FILE = "ValidProTag.txt"

import codecs
from collections import Counter


def replace_same_tag(file_name=SAME_FILE):
    with codecs.open(file_name) as r:
        record_dict = dict()
        curr_dict = dict()
        curr_key = None
        for line in r.readlines():
            curr = line.strip().split('\t')
            if len(curr) == 1:
                if curr_key is not None:
                    record_dict[curr_key] = curr_dict
                curr_key = float(curr[0][1: -1])
                curr_dict = dict()
            else:
                for word in curr[1: ]:
                    curr_dict[word] = curr[0]



if __name__ == "__main__":
    replace_same_tag()
