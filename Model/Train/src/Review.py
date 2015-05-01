# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'
"""
a general class to store review
"""


import simplejson


class Review:
    def __init__(self):
        self.content = str()
        self.jjs = list()
        self.similar_jj = list()
        self.tags = list()
        self.title = str()
        self.type = str()
        self.review_title = str()
        self.users = list()
        self.rate = str()

    def parsefromstring(self, string):
        try:
            data = simplejson.loads(string.lower())
            self.content = data['content'] if 'content' in data else str()
            self.jjs = data['jjs'] if 'jjs' in data else list()
            self.similar_jj = data['similar_jj'] if 'similar_jj' in data else list()
            self.tags = data['tags'] if 'tags' in data else list()
            self.title = data['title'][0] if 'title' in data else str()
            self.type = data['type'] if 'type' in data else str()
            self.review_title = data['review_title'][0] if 'review_title' in data else str()
            self.users = data['users'] if 'users' in data else list()
            self.rate = data['rate'][0] if 'rate' in data else str()
            return self
        except:
            print "not json string when parse from string"
            return self

    def parsefromrawstring(self, string):
        try:
            data = simplejson.loads(string.lower())
            self.content = data['review_text'][-1] if 'review_text' in data else str()
            self.tags = data['pros'] if 'pros' in data else list()
            self.title = data['title'][0] if 'title' in data else str()
            self.review_title = data['review_title'][0] if 'review_title' in data else str()
            self.users = data['best_uses'] if 'best_uses' in data else list()
            self.rate = data['rating'] if 'rating' in data else list()
        except:
            print "not json string when parse from string"

    def is_valid(self):
        if len(self.jjs) == 0:
            return False
        if len(self.tags) == 0:
            return False
        return True


if __name__ == "__main__":
    pass
