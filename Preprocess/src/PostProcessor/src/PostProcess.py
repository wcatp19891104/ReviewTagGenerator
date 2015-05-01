# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'
"""
post process for review
"""


import os
CURR_DICT = os.path.dirname(os.path.realpath(__file__))
import simplejson
import codecs
import sys
import sys
sys.path.insert(0, CURR_DICT + "/../../")
from syname.src.Syname_genetator import Synonyms
from Review import Review


ALL_TAGS = CURR_DICT + "/../resource/ValidProTag.txt"


class PostProcessor:
    def __init__(self, synonym):
        self.synonym = synonym
        self.all_tags = map(lambda x: x.strip().lower().split('\t')[0], codecs.open(ALL_TAGS, encoding='utf-8').readlines())

    def process(self, review):
        for jj in review.jjs:
            if self.synonym.find(jj) != jj:
                review.similar_jj.append(self.synonym.find(jj))
            if jj in self.all_tags:
                review.tags.append(jj)
        for jj in review.similar_jj:
            if jj in self.all_tags:
                review.tags.append(jj)
        remove_set = set()
        for tag in review.tags:
            if tag not in self.all_tags:
                remove_set.add(tag)
        for tag in remove_set:
            review.tags.remove(tag)


if __name__ == "__main__":
    sys = Synonyms()
    r = Review()
    r.tags.append("vergas")
    r.tags.append("easy to wash")
    r.jjs.append("easy")
    post = PostProcessor(sys)
    post.process(r)
    print r.__dict__
    pass