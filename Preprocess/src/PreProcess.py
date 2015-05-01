# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'

"""
Clean training data, seperate them into training data(70%) and test set(30%)
source file: ../resource/babiesrus_review_title.txt
output: train_data.txt, test_data.txt
format review json list:
{
    content:"",
    jjs:[],
    tags:[],
    title:[],
    type:[]
}
Step: 1. read original
      2. extract jj from TagClean.py
      3. find key word from keywordfinder.py
"""

import os
CURR_DICT = os.path.dirname(os.path.realpath(__file__))
from TagClean.src.TagClean import TagClean
from KeyWordFinder.src.KeywordFinder import KeyWordFinder
from syname.src.Syname_genetator import Synonyms
from PostProcessor.src.PostProcess import PostProcessor
import simplejson
import codecs
from Review import Review


SOURCE_TRAIN_FILE = CURR_DICT + "/../resource/babiesrus_review_title.txt"
FORMAT_TRAIN_FILE = CURR_DICT + "/../resource/train_data.txt"
FORMAT_TEST_FILE = CURR_DICT + "/../resource/test_data.txt"


class PreProcess:
    def __init__(self):
        # util of analyze review
        self.tag_cleaner = TagClean()
        self.keyword_finder = KeyWordFinder()
        self.synonymer = Synonyms()
        self.post_processor = PostProcessor(self.synonymer)
        # inner storage
        self.review_list = list()

    def stage_initial(self, review, string):
        review.parsefromrawstring(string)

    def stage_add_jj(self, review):
        review.jjs = self.tag_cleaner.process_single(review.content)[0]

    def stage_add_key_word(self, review):
        self.keyword_finder.fill_review(review)

    def stage_post_process(self, review):
        self.post_processor.process(review)

    def process(self):
        with codecs.open(SOURCE_TRAIN_FILE, encoding='utf-8') as r:
            lines = r.readlines()
            count = 0
            for line in lines:
                print count
                count += 1
                review = Review()
                self.stage_initial(review, line)
                self.stage_add_jj(review)
                self.stage_add_key_word(review)
                self.stage_post_process(review)
                if review.is_valid():
                    self.review_list.append(review)

    def dumps(self):
        train_set = self.review_list[0: int(len(self.review_list) * 0.7)]
        test_set = self.review_list[int(len(self.review_list) * 0.7):]
        with open(FORMAT_TRAIN_FILE, 'w') as w:
            for item in train_set:
                w.write(simplejson.dumps(item.__dict__))
                w.write('\n')
        with open(FORMAT_TEST_FILE, 'w') as w:
            for item in test_set:
                w.write(simplejson.dumps(item.__dict__))
                w.write('\n')

    def run(self):
        self.process()
        self.dumps()


if __name__ == "__main__":
    processer = PreProcess()
    processer.run()
    pass