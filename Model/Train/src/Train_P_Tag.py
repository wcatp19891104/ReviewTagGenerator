# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import os
import codecs
CURR_DICT = os.path.dirname(os.path.realpath(__file__))
import simplejson
from collections import Counter


"""input file"""
Valid_Tag_File = CURR_DICT + "/../resource/ValidProTag.txt"
Train_File = CURR_DICT + "/../resource/train_data.txt"


"""trained file"""
P_Tag = CURR_DICT + "/../dictionary/p_tag.txt"


"""sync dictionary"""
import shutil
shutil.copy(CURR_DICT + '/../../../Preprocess/resource/train_data.txt', Train_File)
shutil.copy(CURR_DICT + '/../../../Preprocess/src/Review.py', CURR_DICT + '/Review.py')


from Review import Review


class TrainPTag:
    def __init__(self):
        self.tag_set = {l.strip().split('\t')[0]: int(l.strip().split('\t')[1]) for l in
                        codecs.open(Valid_Tag_File, encoding='utf-8').readlines()}
        self.data = list()
        self.load()

    def load(self):
        for line in codecs.open(Train_File).readlines():
            curr_r = Review()
            curr_r.parsefromstring(line)
            self.data.append(curr_r)
        print "training data loaded, ", len(self.data)

    def train(self):
        tag_dict = Counter()
        for review in self.data:
            tags = review.tags
            for tag in tags:
                if tag in self.tag_set:
                    tag_dict[tag] += 1
        count = reduce(lambda x, y: x + y[1] if type(x) == int else x[1] + y[1], tag_dict.items())
        p_tag = dict()
        for k, v in tag_dict.items():
            p_tag[k] = v / float(count)
        w = open(P_Tag, 'wb')
        w.write(simplejson.dumps(p_tag))
        w.close()


if __name__ == "__main__":
    t = TrainPTag()
    t.train()
