# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


from BAYES.src.Bayes_Calculator import BayesCalculator
from Train.src.Review import Review
import os
import simplejson
import codecs
from collections import defaultdict


CURR_DICT = os.path.dirname(os.path.realpath(__file__))


"""input file"""
Tag_Category_File = CURR_DICT + '/dictionary/category_of_tags.txt'
Useful_Tag_File = CURR_DICT + '/dictionary/ValidProTag.txt'


class Predictor:
    def __init__(self):
        self.bayes = BayesCalculator()
        self.category_list = list()
        self.tag_category = dict()
        self.valid_tags = set()
        self.load()

    def load(self):
        data = simplejson.loads(codecs.open(Tag_Category_File).read())
        for k, vs in data.items():
            self.category_list.append(k)
            for v in vs:
                self.tag_category[v.strip()] = k
        with codecs.open(Useful_Tag_File) as r:
            for line in r.readlines():
                tag = line.strip().split('\t')[0]
                self.valid_tags.add(tag)

    @staticmethod
    def is_full(my_dict, num):
        for l in my_dict.values():
            if len(l) < num:
                return False
        return True

    def predict(self, review, top_num=3):
        score_board = self.bayes.calculate(review.jjs, review.type)
        score_board = sorted(score_board.items(), key=lambda x: x[1], reverse=True)
        ret_board = dict.fromkeys(self.category_list)
        for key in ret_board:
            ret_board[key] = list()
        for k, v in score_board:
            if self.is_full(ret_board, top_num):
                break
            if k in self.tag_category:
                ret_board[self.tag_category[k]].append(k)
            else:
                print k
        for jj in review.jjs:
            if jj in self.tag_category:
                ret_board[self.tag_category[jj]].insert(0, jj)
        ret_board = {k[0]: k[1][0: top_num] for k in ret_board.items()}
        return ret_board

    def predict_with_probability(self, review, top_num=3):
        score_board = self.bayes.calculate(review.jjs, review.type)
        score_board = sorted(score_board.items(), key=lambda x: x[1], reverse=True)
        ret_board = dict.fromkeys(self.category_list)
        for key in ret_board:
            ret_board[key] = list()
        for k, v in score_board:
            if self.is_full(ret_board, top_num):
                break
            if k in self.tag_category:
                if k == "easy":
                    pass
                ret_board[self.tag_category[k]].append((k, v))
            else:
                print k
        for jj in review.jjs:
            if jj in self.tag_category:
                ret_board[self.tag_category[jj]].insert(0, (jj, 1.0))
                #ret_board[self.tag_category[jj]].insert(0, (jj, ret_board[self.tag_category[jj]][0][1]))
        ret_board = {k[0]: k[1][0: top_num] for k in ret_board.items()}
        for item in ret_board.items():
            title = item[0]
            ans_list = item[1]
            stop_index = len(ans_list)
            for i in range(1, len(ans_list)):
                if ans_list[i][1] > 10 * ans_list[i - 1][1] and ans_list[i][1] != 1.0:
                    stop_index = i
                    break
            ret_board[title] = item[1][0: stop_index]
        return ret_board


if __name__ == "__main__":
    p = Predictor()
    r = Review()
    r.jjs = ['durable']
    r.type = 'diaper'
    #print p.predict(r)
    print p.predict_with_probability(r)
