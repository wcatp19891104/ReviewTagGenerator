__author__ = 'wangzaicheng'
# -*- coding: utf-8 -*-


import unittest
import json

import src.API.analyzer_api


Query_file = "../resource/test/total_product.txt"
Old_file = "../resource/test/old.json"
Difference_file = "../resource/test/difference.txt"
Key_word_set = "../resource/test/key_word_test.txt"
Product_type = "../resource/table/products.txt"
Key_word_failure = "../resource/test/keyword_failure.txt"
New_product_type = "../resource/test/new_products.txt"


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class TestAnalyzerAPI(unittest.TestCase):
    def setUp(self):
        self.query_list = {l.strip() for l in open(Query_file).readlines()}
        self.analyzer = src.API.analyzer_api.Analyzer_API()
        #self.write_back()
        self.old_dict = json.loads(open(Old_file).read())
        self.key_word_dict = self._read_keyword(Key_word_set)
        self.product_type = {l.strip().lower() for l in open(Product_type).readlines()}

    def _read_keyword(self, file_name):
        ret = dict()
        for line in open(file_name).readlines():
            line = line.strip().split('\t')
            if len(line) > 2:
                ret[line[0].replace(':', '')] = line[2].strip()
        return ret

    def test_not_crash(self):
        crash_item = set()
        for query in self.query_list:
            try:
                self.analyzer.index(query)
            except Exception:
                crash_item.add(query)
        msg = '\n'.join(crash_item)
        self.assertEqual(len(crash_item), 0, msg=(str(len(crash_item)) + ' items: \n' + msg + ' crashed'))

    def test_not_too_much_change(self):
        new_dict = dict()
        diff_str = list()
        for query in self.query_list:
            answer_board = list()
            answer_board.append(query)
            new_dict[query] = self.analyzer.to_solr(query)
            new = new_dict[query]
            try:
                old = self.old_dict[query]
            except KeyError:
                continue
            for item in new:
                g = lambda x: '|'.join(x) if type(x) in {set, list} else x
                if item not in old:
                    answer_board.append('\t' + item)
                    answer_board.append('\t\t(new)' + g(new[item]))
                    answer_board.append('\t\t(old)' + "NOT EXIST")
                elif set(new[item]) != set(old[item]):
                    answer_board.append('\t' + item)
                    answer_board.append('\t\t(new)' + g(new[item]))
                    answer_board.append('\t\t(old)' + g(old[item]))
            if len(answer_board) != 1:
                diff_str.append('\n'.join(answer_board))
        open(Difference_file, 'wb').write('-------\n\n' + '\n'.join(diff_str))
        self.assertLessEqual(len(diff_str), 200, msg="too many changes")

    def write_back(self):
        new_dict = dict()
        for query in self.query_list:
            new_dict[query] = self.analyzer.to_solr(query)
        open(Old_file, 'wb').write(json.dumps(new_dict, cls=SetEncoder))

    def test_key_word(self):
        score_board = list()
        not_in_product = set()
        for query in self.key_word_dict:
            correct_key_word = self.key_word_dict[query]
            target_key_word = self.analyzer.to_solr(query)[u'key_words']
            if correct_key_word.lower() != target_key_word.lower():
                score_board.append(query + ":\t" + target_key_word + "-->" + correct_key_word)
                if correct_key_word.lower() not in self.product_type:
                    not_in_product.add(correct_key_word.lower())
        open(Key_word_failure, 'wb').write('\n'.join(score_board))
        open(New_product_type, 'wb').write('\n'.join(not_in_product))
        self.assertEqual(len(score_board), 0, msg="key word error!")


if __name__ == "__main__":
    unittest.main()
    #u = TestAnalyzerAPI()
    #u.write_back()
