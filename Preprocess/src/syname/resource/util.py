# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import os
import simplejson
import codecs


CURR_DICT = os.path.dirname(os.path.realpath(__file__))

#target file
All_words = CURR_DICT + "/allwords.txt"
Target_File = CURR_DICT + "/target.txt"
Word_Frequency_In_Tag = CURR_DICT + "/../resource/word_freq_tag.txt"

#source file
jj_source = CURR_DICT + "/ValidJJ.txt"
tag_source = CURR_DICT + "/ValidProTag.txt"

import collections


def generate_resource():
    """
    generate tables:
    1. allwords.txt: all jjs
    2. target.txt: target of synonyms
    3. word freq: word freq of word occurs in tags
    :return:
    """
    # all words:
    jj_set = dict()
    jj_data = codecs.open(jj_source).readlines()
    for line in jj_data:
        line = line.strip().lower().split('\t')
        jj_set[line[0].split(' ')[-1].strip("'").strip('-').strip('*').strip('..')] = int(line[1])
    w = open(All_words, 'w')
    jj_set = map(lambda x: x[0], sorted(jj_set.items(), key=lambda x: int(x[1]), reverse=True))
    w.write('\n'.join(jj_set))
    # target.txt and target word frequency
    freq_dict = collections.Counter()
    tag_dict = collections.Counter()
    tag_data = codecs.open(tag_source).readlines()
    for line in tag_data:
        line = line.strip().lower().split('\t')
        tag = line[0]
        count = int(line[1])
        tag_dict[tag] += count
        tokens = tag.split(' ')
        for token in tokens:
            freq_dict[token.strip('-').strip('~')] += count
    w = open(tag_source, 'w')
    sorted_tag = sorted(tag_dict.items(), key=lambda x: x[1], reverse=True)
    for tag in sorted_tag:
        w.write(tag[0] + '\t' + str(tag[1]) + '\n')
    w.close()

    w = open(Word_Frequency_In_Tag, 'w')
    w.write(simplejson.dumps(freq_dict))
    w.close()

    w = open(Target_File, 'w')
    w.write('\n'.join(map(lambda x: x[0], freq_dict.items())))
    w.close()


if __name__ == "__main__":
    generate_resource()