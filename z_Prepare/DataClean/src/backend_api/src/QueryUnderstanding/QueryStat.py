__author__ = 'wangzaicheng'

import json
import os
import collections
import requests
import sys

FILE_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, FILE_PATH + '/../')
sys.path.insert(0, FILE_PATH + '/../../')
from src.API import analyzer_api


ABS_PATH = os.path.dirname(os.path.realpath(__file__))
Product_type_file = ABS_PATH + "/../../resource/table/new_products.txt"
solr_url = "http://54.153.90.179:8085/solr/collection1/select?q=*:*&rows=150000&wt=json"
Result_of_type_stat = ABS_PATH + "/../../resource/table/autocomplete_dictionary.txt"
Result_of_type_stat_sorted = ABS_PATH + "/../../resource/analysis/autocomplete_dictionary_sorted.txt"
Change_file = ABS_PATH + '/../../resource/analysis/frequency_change.txt'


class QueryStator:
    def __init__(self):
        self.analyzer = None
        self.title_list = list()
        #self._get_all_title()
        self._remove_list = set()
        self._change_list = dict()
        self._read_change_list()

    def _read_change_list(self, file=Change_file):
        my_map = {'1': 5000, '2': 100, '3': 0}
        for line in open(file).readlines():
            if line[0] == '#':
                continue
            line = line.strip().split('\t')
            try:
                if line[0].lower() in {'add', 'modify'}:
                    self._change_list[line[1].lower()] = my_map[line[2]]
                elif line[0].lower() == 'remove':
                    self._remove_list.add(line[1].lower())
            except:
                continue

    @staticmethod
    def _extract_title(item):
        if u'title' in item:
            return item[u'title']
        if u'product_title' in item:
            return item[u'product_title']
        return None

    def _get_all_title(self):
        data = requests.get(solr_url).text
        data = json.loads(data)
        data = data[u'response'][u'docs']
        for item in data:
            curr_title = self._extract_title(item)
            self.title_list.append(curr_title)
        print "solr data loaded"

    def product_type_stat(self, build_new=False):
        type_counter = collections.Counter()
        brand_counter = collections.Counter()
        if build_new:
            self.analyzer = analyzer_api.Analyzer_API()
            self._get_all_title()
            for p in self.title_list:
                curr_product = self.analyzer.to_solr(p)['product']
                curr_brand = self.analyzer.to_solr(p)['brand']
                for product in curr_product:
                    type_counter[product] += 1
                for brand in curr_brand:
                    brand_counter[brand] += 1
        else:
            for line in open(Result_of_type_stat_sorted).readlines():
                line = line.strip().split('\t')
                type_counter[line[0]] = int(line[1])
        for key in brand_counter:
            if brand_counter[key] >= 6:
                print key
                type_counter.update({key: brand_counter[key]})
        type_counter.update(self._change_list)
        for item in self._remove_list:
            if item in type_counter:
                type_counter.pop(item)
        print "begin sort"
        sorted_number = sorted(type_counter.items(), key=lambda x: x[1], reverse=True)
        sorted_product = sorted(type_counter.items(), key=lambda x: x[0], reverse=True)
        w = open(Result_of_type_stat, 'wb')
        for item in sorted_product:
            try:
                w.write(item[0] + '\t' + str(item[1]) + '\n')
            except:
                w.write(item[0].encode('utf-8') + '\t' + str(item[1]) + '\n')
        w.close()
        w = open(Result_of_type_stat_sorted, 'wb')
        for item in sorted_number:
            try:
                w.write(item[0] + '\t' + str(item[1]) + '\n')
            except:
                w.write(item[0].encode('utf-8') + '\t' + str(item[1]) + '\n')
        w.close()


if __name__ == "__main__":
    q = QueryStator()
    q.product_type_stat(True)
