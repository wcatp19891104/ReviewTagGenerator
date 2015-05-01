# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import os
import simplejson
CURR_DICT = os.path.dirname(os.path.realpath(__file__))
import codecs


"""input data"""
P_Tag_File = 'p_tag.txt'
P_JJ_TAG_FILE = 'p_jj_tag.txt'
P_TYPE_TAG_FILE = 'p_type_tag.txt'
COUNT_TYPE_TAG = 'count_type_tag.txt'
COUNT_JJ_TAG = 'count_jj_tag.txt'


"""sync dictionary"""
import shutil
shutil.copy(CURR_DICT + "/../../Train/dictionary/" + P_JJ_TAG_FILE, CURR_DICT + '/../dictionary/')
shutil.copy(CURR_DICT + "/../../Train/dictionary/" + P_Tag_File, CURR_DICT + '/../dictionary/')
shutil.copy(CURR_DICT + "/../../Train/dictionary/" + P_TYPE_TAG_FILE, CURR_DICT + '/../dictionary/')
shutil.copy(CURR_DICT + "/../../Train/dictionary/" + COUNT_TYPE_TAG, CURR_DICT + '/../dictionary/')
shutil.copy(CURR_DICT + "/../../Train/dictionary/" + COUNT_JJ_TAG, CURR_DICT + '/../dictionary/')


class BayesCalculator:
    def __init__(self, p_tag=P_Tag_File, p_tag_jj=P_JJ_TAG_FILE, p_type_tag=P_TYPE_TAG_FILE,
                 count_type_tag=COUNT_TYPE_TAG, count_jj_tag=COUNT_JJ_TAG):
        self.p_tag = simplejson.loads(codecs.open(CURR_DICT + '/../dictionary/' + p_tag).read())
        self.p_tag_jj = simplejson.loads(codecs.open(CURR_DICT + '/../dictionary/' + p_tag_jj).read())
        self.p_tag_type = simplejson.loads(codecs.open(CURR_DICT + '/../dictionary/' + p_type_tag).read())
        self.count_type_tag = simplejson.loads(codecs.open(CURR_DICT + '/../dictionary/' + count_type_tag).read())
        self.count_jj_tag = simplejson.loads(codecs.open(CURR_DICT + '/../dictionary/' + count_jj_tag).read())

    def calculate(self, jjs, type):
        score_board = dict()
        for tag in self.p_tag:
            curr_score = 1
            count_jj_tag = sum(self.count_jj_tag[tag].values())
            count_type_tag = sum(self.count_type_tag[tag].values())
            for jj in jjs:
                if jj in self.p_tag_jj[tag]:
                    curr_score *= float(self.p_tag_jj[tag][jj])
                else:
                    pass
                    curr_score *= 0.001 / float(count_jj_tag)
                if type in self.p_tag_type[tag]:
                    curr_score *= float(self.p_tag_type[tag][type])
                else:
                    pass
                    curr_score *= 0.001 / float(count_type_tag)
                #curr_score *= self.p_tag[tag]
            score_board[tag] = curr_score * self.p_tag[tag]
        return score_board


if __name__ == "__main__":
    b = BayesCalculator()
    print b.calculate(['importantly', 'common', 'written'], 'diaper')
    pass