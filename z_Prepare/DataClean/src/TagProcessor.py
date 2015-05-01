__author__ = 'wangzaicheng'


import collections
import codecs


class TagProcessor:
    def __init__(self, name=None):
        self.name = name
        self.con_stack = list()
        self.pro_stack = list()
        self.activate = False

    def process(self, tag_name, tag_label):
        self.con_stack.append(tag_name)

    def get_stack(self):
        return self.pro_stack, self.con_stack


class AgeProcessor(TagProcessor):
    def __init__(self):
        TagProcessor.__init__(self, "AgeProcess")

    def process(self, tag_name, tag_label):
        if tag_label == "CD":
            self.activate = True
            self.con_stack.append(tag_name)
            return
        elif tag_name == 'old':
            self.con_stack.append(tag_name)
            self.activate = False
            return

    def __iter__(self):
        return


class NegProcessor(TagProcessor):
    def __init__(self):
        TagProcessor.__init__(self, "NegProcess")
        self.not_set = {l.strip() for l in codecs.open("../dictionary/negative_word.txt", encoding='utf-8').readlines()}
        self.mode_change = {l.strip() for l in codecs.open("../dictionary/change.txt", encoding='utf-8').readlines()}

    def process(self, tag_name, tag_label):
        if not self.activate:
            return
        if tag_name in self.not_set:
            self.activate = True
            return
        if tag_name in self.mode_change:
            self.activate = False
        else:
            self.con_stack.append('not ' + tag_name)


