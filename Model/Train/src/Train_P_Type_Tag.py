# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import codecs
import os
import simplejson
import collections


CURR_DICT = os.path.dirname(os.path.realpath(__file__))


"""input file"""
Train_File = CURR_DICT + "/../resource/train_data.txt"


"""trained file"""
P_type_Tag = CURR_DICT + "/../dictionary/p_type_tag.txt"
Count_Type_Tag = CURR_DICT + "/../dictionary/count_type_tag.txt"

"""sync dictionary"""
import shutil
shutil.copy(CURR_DICT + '/../../../Preprocess/resource/train_data.txt', Train_File)
shutil.copy(CURR_DICT + '/../../../Preprocess/src/Review.py', CURR_DICT + '/Review.py')


from Review import Review


class TrainTypeTag:
    def __init__(self):
        self.data = list()
        self.load()

    def load(self):
        for line in codecs.open(Train_File).readlines():
            curr_r = Review()
            curr_r.parsefromstring(line)
            self.data.append(curr_r)
        print "training data loaded, ", len(self.data)

    def train(self):
        count_tag_type = collections.defaultdict(collections.Counter)
        p_tag_type = collections.defaultdict(dict)
        for review in self.data:
            curr_type = review.type
            tag_list = review.tags
            for tag in tag_list:
                count_tag_type[tag][curr_type] += 1
        for k, v in count_tag_type.items():
            curr_sum = reduce(lambda x, y: x + y[1] if type(x) == int else x[1] + y[1], v.items())
            for w, w_c in v.items():
                p_tag_type[k][w] = w_c / float(curr_sum)
        w = open(P_type_Tag, 'wb')
        w.write(simplejson.dumps(p_tag_type))
        w.close()
        w = open(Count_Type_Tag, 'wb')
        w.write(simplejson.dumps(count_tag_type))
        w.close()


if __name__ == "__main__":
    t = TrainTypeTag()
    t.train()