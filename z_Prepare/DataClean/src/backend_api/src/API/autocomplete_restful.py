# -*- coding: utf-8 -*-
__author__ = 'skwek'
import cherrypy
import operator
import cherrypy_cors
cherrypy_cors.install()
import json
import sys
import os
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, FILE_PATH + '/../')
sys.path.insert(0, FILE_PATH + '/../../')
from src.QueryUnderstanding.QueryStat import QueryStator

MAX_AUTOCOMPLETION = 5
"""
A fast data structure for searching strings with autocomplete support.
"""

class Trie(object):
    DICTIONARY = FILE_PATH + "/../../resource/table/autocomplete_dictionary.txt"
    text_weight = {}
    def __init__(self):
        self.children = {}
        self.weight = {}
        self.flag = False # Flag to represent that a word ends at this node

    def _initialize_root(self):
        for line in open(Trie.DICTIONARY):
            text, weight = line.strip().split('\t')
            text = text.lower()
            weight = int(weight)
            self.insert(text, weight)

    def add(self, char):
        self.children[char] = Trie()


    def insert(self, word, weight):
        #print word, weight
        Trie.text_weight[word] = weight
        node = self
        for char in word:
            if char not in node.children:
                node.add(char)
            node = node.children[char]
        node.flag = True

    def contains(self, word):
        node = self
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.flag

    def all_suffixes(self, prefix):
        results = set()
        if self.flag:
            results.add(prefix)
        if not self.children: return results
        return reduce(lambda a, b: a | b, [node.all_suffixes(prefix + char) for (char, node) in self.children.items()]) | results

    @cherrypy.expose
    def autocomplete(self, prefix, max_results = MAX_AUTOCOMPLETION, **params):
        if type(max_results) in [str, unicode]:
            if max_results.isdigit():
                max_results = int(max_results)
            else:
                max_results = MAX_AUTOCOMPLETION
        prefix = prefix.lower()
        node = self
        for char in prefix:
            if char not in node.children:
                return '[]'
            node = node.children[char]
        weighted_suffixes = dict((w, Trie.text_weight[w]) for w in node.all_suffixes(prefix))
        data = json.dumps(list(tup[0] for tup in sorted(weighted_suffixes.items(), key = operator.itemgetter(1), reverse=True)[:max_results]))
        #return json.loads(data)
        if 'callback' in params:
            return params['callback'] + '(' + data + ')'
        return data

if __name__ == '__main__':
    #update table before every start, added by zaicheng
    q = QueryStator()
    q.product_type_stat()
    conf = {
        '/': {
            'tools.sessions.on': True,
            'server.max_request_body_size': 0,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/javascript')],
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8108,
        'server.max_request_body_size': 0
    })
    trie = Trie()
    trie._initialize_root()
    #print trie.autocomplete("dia")
    #trie.autocomplete('dia', max_results=7)
    cherrypy.quickstart(trie, '/', conf)
