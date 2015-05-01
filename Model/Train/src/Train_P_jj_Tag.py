# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import codecs
import os
import simplejson
import collections


CURR_DICT = os.path.dirname(os.path.realpath(__file__))


"""input file"""
Valid_JJ_File = CURR_DICT + "/../resource/ValidJJ.txt"
Train_File = CURR_DICT + "/../resource/train_data.txt"


"""trained file"""
P_jj_Tag = CURR_DICT + "/../dictionary/p_jj_tag.txt"
Count_JJ_Tag = CURR_DICT + '/../dictionary/count_jj_tag.txt'


"""sync dictionary"""
import shutil
shutil.copy(CURR_DICT + '/../../../Preprocess/resource/train_data.txt', Train_File)
shutil.copy(CURR_DICT + '/../../../Preprocess/src/Review.py', CURR_DICT + '/Review.py')


from Review import Review


class TrainJJTag:
    def __init__(self):
        self.jj_set = {l.strip().split('\t')[0] for l in codecs.open(Valid_JJ_File, encoding='utf-8').readlines()}
        self.data = list()
        self.load()

    def load(self):
        for line in codecs.open(Train_File).readlines():
            curr_r = Review()
            curr_r.parsefromstring(line)
            self.data.append(curr_r)
        print "training data loaded, ", len(self.data)

    def train(self):
        count_tag_jj = collections.defaultdict(collections.Counter)
        p_tag_jj = collections.defaultdict(dict)
        for review in self.data:
            jj_list = review.jjs
            tag_list = review.tags
            for tag in tag_list:
                for jj in jj_list:
                    if jj in self.jj_set:
                        count_tag_jj[tag][jj] += 1
        for k, v in count_tag_jj.items():
            curr_sum = reduce(lambda x, y: x + y[1] if type(x) == int else x[1] + y[1], v.items())
            for w, w_c in v.items():
                p_tag_jj[k][w] = w_c / float(curr_sum)
        w = open(P_jj_Tag, 'wb')
        w.write(simplejson.dumps(p_tag_jj))
        w.close()
        w = open(Count_JJ_Tag, 'wb')
        w.write(simplejson.dumps(count_tag_jj))
        w.close()

if __name__ == "__main__":
    t = TrainJJTag()
    t.train()
