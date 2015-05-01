# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'

import codecs
import nltk
#from Preprocess.src.TagClean.src import TagProcessor, MyTagger
import TagProcessor
import MyTagger
import os


CURR_DICT = os.path.dirname(os.path.realpath(__file__))


class TagClean:
    def __init__(self):
        self.send_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tagger = MyTagger.MyTagger()
        self.cons = list()
        self.pros = list()
        self.valid_words = {l.strip() for l in codecs.open(CURR_DICT + '/../dictionary/allEnglishWords.txt',
                                                           encoding='utf-8').readlines()}

        self.not_set = {l.strip() for l in codecs.open(CURR_DICT + "/../dictionary/negative_word.txt",
                                                       encoding='utf-8').readlines()}

        self.mode_change = {l.strip() for l in codecs.open(CURR_DICT + "/../dictionary/change.txt",
                                                           encoding='utf-8').readlines()}

        self.useful_field = {l.strip() for l in codecs.open(CURR_DICT + '/../dictionary/emotion_list.txt',
                                                            encoding='utf-8').readlines() if l.strip()[0] != '#'}

        self.emotion_except = {l.strip() for l in codecs.open(CURR_DICT + '/../dictionary/neutral_word.txt',
                                                              encoding='utf-8').readlines() if l.strip()[0] != '#'}

    def tag_process(self, tags):
        neg_stack = list()
        ret_stack = list()
        neg_mode = False
        #TODO: add processors
        #TODO: 1. 转折词看待成分句子
        #real emotion is JJ, CD should be not inclued
        test_processor0 = TagProcessor.TagProcessor()
        test_processor1 = TagProcessor.AgeProcessor()
        test_processor2 = TagProcessor.NegProcessor()
        for tag in tags:
            curr_word = tag[0]
            curr_label = tag[1]
            if curr_label not in self.useful_field:
                continue
            if curr_word in self.emotion_except:
                continue
        #     test_processor1.process(curr_word, curr_label)
        #     test_processor2.process(curr_word, curr_label)
        #     test_processor0.process(curr_word, curr_label)
        # ret = test_processor0.get_stack()[1]
        # for tag in test_processor1.get_stack()[1]:
        #     ret.remove(tag)
        #     pass
        # for tag in test_processor2.get_stack()[1]:
        #     ret.remove(tag[4: ])
        #     ret.append(tag)
        # return ret
            if neg_mode:
                if curr_word in self.mode_change:
                    ret_stack.extend(neg_stack)
                    neg_stack = list()
                    neg_mode = False
                else:
                    neg_stack.append('not ' + curr_word)
            else:
                if curr_word in self.not_set:
                    neg_mode = True
                else:
                    ret_stack.append(curr_word)

        ret_stack.extend(neg_stack)
        return ret_stack

    def process_single(self, string):

        """

        :param string: a single review
        :return: pro_list: a list of positive words
                con_list: a list of negative words
        """
        pos_list = list()
        con_list = list()
        sents = self.send_detector.tokenize(string.lower())
        for sent in sents:
            try:
                tokens = nltk.word_tokenize(sent)
                tags = self.tagger.tag(tokens)
                con_list.extend(self.tag_process(tags))
            except:
                print "special character detected! ",string
        remove_set = set()
        for con in con_list:
            if con not in self.valid_words and con.split(' ')[-1] not in self.valid_words:
                remove_set.add(con)
        for r in remove_set:
            con_list.remove(r)
        return con_list, pos_list


if __name__ == "__main__":
    cleaner = TagClean()
    print cleaner.process_single("This can be used facing back and front and will get me through all growing stages. This grandmother is thinking ahead,that's what we do best!! Love the two cup holders,one for drink and other for Cheerios snack.")


