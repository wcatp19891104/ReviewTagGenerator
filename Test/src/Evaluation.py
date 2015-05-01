# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import codecs
import os
import sys
from collections import Counter
CURR_DICT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, CURR_DICT + '/../../')
from Model.predict import Predictor
from Model.Train.src.Review import Review


"""input file"""
TEST_SET_FILE = CURR_DICT + '/../resource/test_data.txt'
#TEST_SET_FILE = CURR_DICT + '/../resource/train_data.txt'
"""sync file"""
import shutil
shutil.copy(CURR_DICT + '/../../Preprocess/resource/test_data.txt', TEST_SET_FILE)


class Tester:
    def __init__(self, test_set_num=-1):
        self.data = list()
        self.load(test_set_num)
        self.predictor = Predictor()

    def load(self, test_set_num):
        for line in codecs.open(TEST_SET_FILE).readlines()[0: test_set_num]:
            curr_r = Review()
            curr_r.parsefromstring(line)
            self.data.append(curr_r)
        print "test data loaded, ", len(self.data)

    def evaluate(self):
        right = 0
        wrong = 0
        for review in self.data:
            if review.type != "diaper":
                continue
            category_dict = self.predictor.predict(review, 1)
            values = list()
            for value in category_dict.values():
                values.extend(value)
            if len(set(values).intersection(set(review.tags))) > 0:
                #print len(set(values).intersection(set(review.tags)))
                right += 1
            else:
                wrong += 1
            print right + wrong
        print right / float(right + wrong)

    def diversity_evaluation(self, product_type=None):
        tag_counter = list()
        for review in self.data:
            if review.type != product_type and product_type is not None:
                continue
            category_dict = self.predictor.predict(review, 3)
            values = list()
            for value in category_dict.values():
                values.extend(value)
            tag_counter.append(values[0])
        tag_counter = Counter(tag_counter)
        print tag_counter
        print len(tag_counter)

    def evaluate_with_probability(self, top_num=1):
        right = 0
        wrong = 0
        for review in self.data:
            if review.type != "diaper":
                #continue
                pass
            category_dict = self.predictor.predict_with_probability(review, top_num)
            score_board = list()
            for i in range(top_num):
                curr_score = list()
                for item in category_dict.values():
                    curr_score.append(item[0])
                curr_score = map(lambda x: x[0], sorted(curr_score, key=lambda x: x[1], reverse=True))
            score_board.extend(curr_score)
            #category_dict = self.predictor.predict(review, 1)
            values = list()
            for value in category_dict.values():
                values.extend(value)
            #values = score_board[0: len(review.tags)]
            #values = score_board[0: 3]
            values = score_board[0:3]
            # print values
            # print review.tags
            #print "-------------------------------"
            if len(set(values).intersection(set(review.tags))) > 0:
                #print len(set(values).intersection(set(review.tags)))
                right += 1
            else:
                print values
                print review.tags
                print "-------------------------------"
                wrong += 1
            #print right + wrong
        print right / float(right + wrong)

if __name__ == "__main__":
    t = Tester()
    t.diversity_evaluation('stroller')
    #t.evaluate()
    t.evaluate_with_probability(3)