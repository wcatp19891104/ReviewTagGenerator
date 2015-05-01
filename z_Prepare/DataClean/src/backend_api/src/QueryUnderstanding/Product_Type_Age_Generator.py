__author__ = 'wangzaicheng'
# -*- coding: utf-8 -*-


import os
import collections


ABS_PATH = os.path.dirname(os.path.realpath(__file__))
#Type_Age_File = '/'.join(ABS_PATH.split('/')[: -1]) + "/resource/table/type_age_mapping.txt"
Type_Age_File = ABS_PATH + '/../../resource/table/type_age_mapping.txt'


class AgeGenerator:
    def __init__(self):
        self.age_map = collections.defaultdict(set)
        self.read_age_map()

    def read_age_map(self):
        for line in open(Type_Age_File).readlines():
            line = line.strip().split('->')
            for item in line[1].split(','):
                self.age_map[item.strip()].add(line[0].strip())

    def get_range(self, word):
        ret = set()
        #word = set(word.split(' '))
        word_list = set(word.split(' '))
        for token in self.age_map:
            if len(token.split(' ')) == 1:
                if token in word_list:
                    ret = ret.union(self.age_map[token])
            else:
                if token in word:
                    ret = ret.union(self.age_map[token])
        return ret


if __name__ == "__main__":
    a = AgeGenerator()
    print a.get_range('Dreambaby L330 Essential Grooming Kit 10 Pieces Aqua')
