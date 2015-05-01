# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'
"""
find a valid synonys given a word
init: initialize
stem: stem a word
API_generator: rolling api
api_process: fetching data from api
train: making table for synonyms
find: find a valid synonys else itself
"""

import requests
import os
import sys
import codecs
import simplejson
import collections
from nltk.stem.porter import *
from itertools import cycle


CURR_DICT = os.path.dirname(os.path.realpath(__file__))
Synonyms_FILE = CURR_DICT + "/../resource/synonyms_dict.txt"
All_words = CURR_DICT + "/../resource/allwords.txt"
Target_File = CURR_DICT + "/../resource/target.txt"
Word_Frequency_In_Tag = CURR_DICT + "/../resource/word_freq_tag.txt"
API_1 = 'http://thesaurus.altervista.org/thesaurus/v1?word={0}&output=json&key=xxZOdv9jRtZ4jxsAOwDE&language=en_US'
API_2 = 'http://thesaurus.altervista.org/thesaurus/v1?word={0}&output=json&key=4AQD3coW5yqSmmJLW4mI&language=en_US'


class Synonyms:
    def __init__(self, train=False, start=0, end=-1):
        self.curr = True
        self.look_up = collections.defaultdict(set)
        self.stemmer = PorterStemmer()
        self.target_freq = simplejson.loads(codecs.open(Word_Frequency_In_Tag).read())
        #self.target_freq = dict()
        self.init()
        self.target = {l.strip().lower() for l in codecs.open(Target_File).readlines()}
        if train:
            self.train(start, end)

    def init(self):
        if os.path.isfile(Synonyms_FILE):
            self.look_up = simplejson.loads(open(Synonyms_FILE).read())
        else:
            pass

    def stem(self, word):
        return self.stemmer.stem(word)

    def API_generator(self):
        while True:
            if self.curr:
                self.curr = False
                yield API_1
            else:
                self.curr = True
                yield API_2

    def api_process(self, word):
        try:
            data = requests.get(self.API_generator().next().format(word)).text
            data = simplejson.loads(data)
            ret = list()
            useful_data = data['response']
            for entry in useful_data:
                curr_tag = entry['list']['category'].lstrip('(').rstrip(')')
                curr_synonyms = [self.stem(l.strip()) for l in entry['list']['synonyms'].split('|')
                                 if '(' not in l and ')' not in l and len(l.split(' ')) == 1]
                #TODO 现在是返回所有的同义词不管词性，将来可能会有所更改, marked
                ret.extend(curr_synonyms)
            return ret
        except:
            print 'error: sysnonyms', word
            return []

    def train(self, start=0, end=-1):
        word_set = {l.strip().lower() for l in codecs.open(All_words).readlines()[start: end]}
        count = 0
        for word in word_set:
            if word not in self.look_up:
                synonyms = self.api_process(word)
                print count
                count += 1
                self.look_up[word] = synonyms
        w = open(Synonyms_FILE, "w")
        w.write(simplejson.dumps(self.look_up))
        w.close()

    def find(self, word):
        prefix = ""
        if word.split(' ')[0] == 'not':
            prefix = 'not '
            word = word.split(' ')[1]
        if word in self.look_up:
            candidate = self.look_up[word]
        else:
            candidate = self.api_process(word)
        possible = set()
        for cand in candidate:
            if cand in self.target:
                possible.add(prefix + cand)
        if len(possible) != 0:
            ret = max(possible, key=lambda x: self.target_freq[x] if x in self.target_freq else 0)
            return ret
        return prefix + word

if __name__ == "__main__":
    syn = Synonyms()
    print syn.find("quickly")
