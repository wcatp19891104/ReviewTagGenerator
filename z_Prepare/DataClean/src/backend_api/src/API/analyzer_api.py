# -*- coding: utf-8 -*-
__author__ = 'skwek'

import __init__
import os
import collections
import cherrypy
from json2html import *
from cherrypy.lib import static
import sys


ABS_PATH = os.path.dirname(os.path.realpath(__file__))
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, FILE_PATH + '/../')
sys.path.insert(0, FILE_PATH + '/../../')
from src.QueryUnderstanding import analyzer
from src.QueryUnderstanding.Product_Type_Age_Generator import AgeGenerator

UI_page = ABS_PATH + '/../../resource/webpage/test.html'
abs_dir = os.path.join(os.getcwd(), os.path.dirname(__file__))
useful_tag = {'brand', 'product', 'color', 'series_model', 'characters', 'age_low', 'age_high', 'stop_word',
              'store_name',}


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Analyzer_API:
    def __init__(self):
        self._analyzer = analyzer.Analyzer()
        self._age_generator = AgeGenerator()
        self._result_file_name = None

    @staticmethod
    def _age_range_assign(json_data):
        low = int(list(json_data['age_low'])[0]) if json_data['age_low'] != set() else -1
        high = int(list(json_data['age_high'])[0]) if json_data['age_high'] != set() else 10000
        #age_dict = [(range(0, 7), "0-6 month"), (range(6, 19), "6-18 month"), (range(18, 25), "18-24 month"),
        #            (range(24, 37), "2T-3T"), (range(36, 49), "3T-4T"), (range(48, 61), "4T-5T"), (range(60), "5+")]
        age_dict = [(range(0, 7), "0006"), (range(6, 19), "0618"), (range(18, 25), "1824"),
                    (range(24, 37), "2436"), (range(36, 49), "3648"), (range(48, 61), "4860"), (range(60), "6000")]
        if low == -1 and high == 10000:
            return []
        if low > 60:
            return ["5+"]
        ret = list()
        for age in age_dict:
            if low in age[0] and high in age[0]:
                return [age[1]]
            elif low in age[0]:
                ret.append(age[1])
            elif high in age[0]:
                ret.append((age[1]))
                return ret
            elif len(ret) != 0:
                ret.append(age[1])
        return ret

    def _to_format(self, result):
        #result = json.loads(result)
        json_data = collections.defaultdict(set)
        for tag in useful_tag:
            json_data[tag] = set()
        for item in result['word_tag'].items():
            overlap = set(item[1]).intersection(useful_tag)
            for tag in overlap:
                json_data[tag.strip()].add(item[0].strip())
        json_data['key_words'] = result['key_word'].strip()
        json_data['product_type_id'] = result['product_type_id']
        json_data['key_words_id'] = result['key_word_id']
        json_data['brand_id'] = result['brand_id']
        json_data['gender'] = result['gender']
        json_data['age_range'] = self._age_range_assign(json_data)
        json_data['age_range'] = list(set(json_data['age_range']).union(self._age_generator.get_range(result['normalized phrase'].lower())))
        #json_data['age_range'] = self._age_range_assign(json_data)
        json_data['normalized_query'] = result['normalized phrase']
        json_data['store_name'] = json_data['store_name'].pop() if len(json_data['store_name']) != 0 else ""
        json_data['useful'] = self.is_useful(json_data)
        json_data['quantity'] = result['quantity'][0]
        json_data['quantity_unit'] = result['quantity'][1]
        return json.dumps(json_data, cls=SetEncoder)

    @staticmethod
    def is_useful(json_data):
        default_array = {'product', 'characters', 'brand_id', 'color', 'brand', 'age_range', 'store_name',
                         'series_model', 'product_type_id'}
        for item in default_array:
            if len(json_data[item]) != 0:
                return '1'
        if json_data['key_words_id'] != "TBD":
            return '1'
        return '0'

    def to_solr(self, text):
        #print "analyzing" + text
        result = self._analyzer.analyze(text)
        json_data = collections.defaultdict(set)
        for tag in useful_tag:
            json_data[tag] = set()
        for item in result['word_tag'].items():
            overlap = set(item[1]).intersection(useful_tag)
            for tag in overlap:
                json_data[tag.strip()].add(item[0].strip())
        json_data['key_words'] = result['key_word'].strip()
        json_data['product_type_id'] = result['product_type_id']
        json_data['key_words_id'] = result['key_word_id']
        json_data['brand_id'] = result['brand_id']
        json_data['gender'] = result['gender']
        json_data['age_range'] = self._age_range_assign(json_data)
        json_data['age_range'] = list(set(json_data['age_range']).union(self._age_generator.get_range(text.lower())))
        json_data['normalized_query'] = result['normalized phrase']
        json_data['store_name'] = json_data['store_name'].pop() if len(json_data['store_name']) != 0 else ""
        json_data['useful'] = self.is_useful(json_data)
        json_data['quantity'] = result['quantity'][0]
        json_data['quantity_unit'] = result['quantity'][1]
        #print "finishing analyzing" + text
        return json_data

    @cherrypy.expose
    def index(self, query):
        return self._to_format(self._analyzer.analyze(query))

    @cherrypy.expose
    def analysis(self, text=''):
        json_data = json.dumps(self._analyzer.analyze(text))
        json_data = json_data.replace('\u00a0', ' ')
        #json_data = json_data.encode('utf-8')
        try:
            json_display = json2html.convert(json=json_data)
        except StandardError:
            json_display = json_data
        return open(UI_page).read().format(text.encode('utf-8'), json_display)

    @cherrypy.expose
    def analysis_batch(self, query_file):
        output_file = abs_dir + 'output.txt'
        w = open(output_file, 'wb')
        cherrypy.response.timeout = 7200
        for line in query_file.file.readlines():
            print line
            data = json.loads(json.dumps(self._analyzer.analyze(line.strip())), object_pairs_hook=collections.OrderedDict)
            try:
                w.write(data['original phrase'].encode('utf-8') + ':\n')
            except StandardError:
                w.write(data['original phrase'].encode('latin-1') + ':\n')
            w.write('\tword_tag:\n')
            for item in data['word_tag'].items():
                l = [b.encode('utf-8') for b in item[1]]
                w.write('\t\t' + item[0].encode('utf-8') + '\t' + '/'.join(l) + '\n')
            w.write('\tkey_word\t\n')
            w.write('\t\t' + data['key_word'].encode('utf-8') + '\n')
            w.write('\tquery categorization:\n')
            #for item in data['query categorization']:
            #    w.write('\t\t' + item.encode('utf-8') + '\n')
            w.write('\tsynonyms\n')
            for item in data['synonyms'].items():
                l = [b.encode('utf-8') for b in item[1]]
                w.write('\t\t' + item[0].encode('utf-8') + '\t' + '/'.join(l) + '\n')

        w.close()
        self._result_file_name = output_file
        return self.download()

    @cherrypy.expose()
    def type(self, word, mode="net"):
        result = json.loads(self._to_format(self._analyzer.analyze(word)))
        if mode == "package":
            return result['product'], result['product_type_id'], result['brand_id'], [result['key_words_id']], result['age_range']
        elif mode == "net":
            return json.dumps([result['product'], result['product_type_id'], result['brand_id'],
                               [result['key_words_id']], result['age_range']])
        #return json.dumps(result['product'])

    @cherrypy.expose()
    def download(self):
        return static.serve_file(self._result_file_name, "application/x-download",
                                 "attachment", os.path.basename(self._result_file_name))


if __name__ == "__main__":
    # a = Analyzer_API()
    # print a.to_solr("BreathableBaby - Breathable Crib Liner 18 pack, Fits All Cribs, Available in Multiple Colors")
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8082,
        'server.max_request_body_size': 0
    })

    cherrypy.quickstart(Analyzer_API(), '/')
