# -*- coding: utf-8 -*-

import os
import json
from collections import defaultdict, OrderedDict

from src.QueryUnderstanding import plur2sing
from src.QueryUnderstanding.Product_Type_Id_Generator import ID_generator
from ActionAndRule import Rule, AgeRule, Range, RangeAge, RangeRule, match_quantity_and_unit


R_weight = Rule('^\d+( *)(lb|kg)$', 'weight')
R_age = AgeRule('^(\d+)( *)(year|month|year old|t|m|mon)$', 'age_low')
R_length = Rule('^\d+( *)(in|inch|")$', 'length')
R_integer = Rule('^\d+$', 'integer')
R_price = Rule('^\$\d+(\.\d\d)?$', 'price')
R_measure = Rule('^\d+( *)(pack|packs|sheets|sheet)$', 'measurement')
R_range = Range('^(\d+)( *)(-|to| )( *)(\d+)$', 'range')
R_age_range = RangeAge('^(\d+)( *)( *|year|month|year old|t|T|m|mon)( *)(-|to| )( *)(\d+)( *)(year|month|year old|t|T|m|mon)$', 'age range')
#R_baby_apparel_size_range = RangeRule('^(\d+)( *)(t|T)( *)(-|to)( *)(\d+)( *)(t|T)$', 'babies_apparel_size range')
R_weight_range = RangeRule('^(\d+)( *)(lb|kg)( *)(-|to| )( *)(\d+)( *)(lb|kg)$', 'weight range')
R_length_range = RangeRule('^(\d+)( *)(in|inch)( *)(-|to| )( *)(\d+)( *)(in|inch)$', 'length range')
Key_word_exception = {'box', 'set', 'kit', 'pack', 'combo', 'capsule'}


class OrderedDefaultDict(OrderedDict, defaultdict):
    pass


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Analyzer:
    ABS_PATH = os.path.dirname(os.path.realpath(__file__))
    #QUERY_DIR = ABS_PATH + '/resources/Data/queries/'
    RESOURCE_DIR = ABS_PATH + '/../../resource/table/'

    def __init__(self):
        self._ID_generator = ID_generator()
        self._ID_generator.refresh()
        self._seperate_word = {'for', 'with', 'to', 'in', 'on', '-', '//', '/', '/w', '(', ',', 'plus', ';'}
        self._normalizer = plur2sing.Plur2Sing()
        self._word_tag_map = OrderedDefaultDict()
        self._word_tag_map.default_factory = set
        self._tag_pattern = dict()
        self._brand_mapping = dict()
        self._store_mapping = dict()
        self._product_hierarchy = defaultdict(lambda: 0)
        self._unit_set = set()
        self._denormalize = dict()
        self._brand_model = defaultdict(set)
        self._model_brand = defaultdict(set)
        self._gender_map = dict()
        self._read_brand_mapping(Analyzer.RESOURCE_DIR + 'brand_model_mapping.txt')
        self._word_tag_map['store_name'] = self._read_store(Analyzer.RESOURCE_DIR + 'store_name_map.txt')
        self._word_tag_map['demography'] = self._read_dict(Analyzer.RESOURCE_DIR + 'demography.txt')
        self._word_tag_map['product'] = self._read_dict(Analyzer.RESOURCE_DIR + 'new_products.txt')
        self._word_tag_map['stop_word'] = self._read_dict(Analyzer.RESOURCE_DIR + 'stopwords.txt')
        # self._word_tag_map['brand'] = self._read_dict(Analyzer.RESOURCE_DIR + 'taxonomy2/brand_dictionary.txt')
        self._word_tag_map['brand'] = self._read_brand(Analyzer.RESOURCE_DIR + 'brands.txt')\
            .union(set(self._brand_model.keys()))
        self._word_tag_map['color'] = self._read_dict(Analyzer.RESOURCE_DIR + 'colors.txt')
        # self._word_tag_map['series_model'] = self._read_dict(Analyzer.RESOURCE_DIR + 'taxonomy/series_model.txt')
        self._word_tag_map['characters'] = self._read_dict(Analyzer.RESOURCE_DIR + 'character.txt')
        self._big_map = self._combine_dict()
        self._read_gender(Analyzer.RESOURCE_DIR + 'gender_dictionary.txt')
        self._type_id = self._read_dict_from_table(Analyzer.RESOURCE_DIR + 'product_id_mapping.txt')
        self._read_dict_from_pair(Analyzer.RESOURCE_DIR + 'taxonomy.txt')
        self._read_unit_from_file(Analyzer.RESOURCE_DIR + 'unit.txt')
        self._read_hierarchy(Analyzer.RESOURCE_DIR + 'productkeyword_hierarchy.txt')
        self._synonyms = []
        self._synonym_map = defaultdict(set)

        # zaicheng added
        self._not_search = defaultdict(list)
        for line in open(self.RESOURCE_DIR + 'overlap_list.txt').readlines():
            key = line.strip().split('\t')[0]
            item = line.strip().split('\t')[1]
            self._not_search[key] = item.split('|')

        for line in open(Analyzer.RESOURCE_DIR + 'synonyms.txt'):
        # for line in open(Analyzer.RESOURCE_DIR + 'TEMP/sysnonyms.txt'):
            if line.find('=>') != -1:
                key, syn = line.strip().split('=>')
                self._synonyms.append(set(syn.split(',')))
                index = len(self._synonyms) - 1
                for w in syn.split(','):
                    self._synonym_map[w].add(index)

        self._pattern_list = list()
        self._pre_pattern_list = list()
        self._pre_pattern_list.append(R_measure)
        # self._pattern_list.append(R_baby_apparel_size)
        self._pattern_list.append(R_weight)
        self._pattern_list.append(R_age)
        self._pattern_list.append(R_length)
        self._pattern_list.append(R_integer)
        self._pattern_list.append(R_price)
        self._pattern_list.append(R_range)
        self._pattern_list.append(R_age_range)
        # self._pattern_list.append(R_baby_apparel_size_range)
        self._pattern_list.append(R_weight_range)
        self._pattern_list.append(R_length_range)

    def _combine_dict(self):
        _big_map = defaultdict(set)
        for item in self._word_tag_map.items():
            for cell in item[1]:
                _big_map[cell].add(item[0])
        return _big_map

    def _read_gender(self, filename):
        for line in open(filename):
            if line[0] == '#':
                continue
            line = line.split(":")
            gender = line[0]
            for word in line[1].split(','):
                self._gender_map[word.strip()] = gender

    def _read_store(self, filename):
        for line in open(filename):
            line = line.strip().split('\t')
            for item in line:
                if line != "":
                    self._store_mapping[self._normalizer.normalize_line(item)] = self._normalizer.normalize_line(line[0])
                    self._denormalize[self._normalizer.normalize_line(item)] = item.strip()
                    self._denormalize[self._normalizer.normalize_line(line[0])] = line[0].strip()
        return set(self._store_mapping.keys())

    def _read_brand(self, filename):
        for line in open(filename):
            line = line.strip().split('\t')
            for item in line:
                if item != "":
                    self._brand_mapping[self._normalizer.normalize_line(item)] = \
                        self._normalizer.normalize_line(line[0])
                    self._denormalize[self._normalizer.normalize_line(item)] = item.strip()
                    self._denormalize[self._normalizer.normalize_line(line[0])] = line[0].strip()
        return set(self._brand_mapping.keys())

    def _read_brand_mapping(self, filename):
        for line in open(filename):
            line = line.strip().split('\t')
            for item in line[1:]:
                self._brand_model[self._normalizer.normalize_line(line[0])].\
                    add(self._normalizer.normalize_line(item.strip()))
                self._brand_mapping[self._normalizer.normalize_line(line[0])] = self._normalizer.normalize_line(line[0])
                self._model_brand[self._normalizer.normalize_line(item.strip())].\
                    add(self._normalizer.normalize_line(line[0]))

    def _read_hierarchy(self, file_name):
        for line in open(file_name).readlines():
            line = line.strip().split('\t')
            self._product_hierarchy[line[0]] = int(line[1])
            #self._product_hierarchy[line[0]] = 0

    def _match_re_pattern(self, _p, result):
        pattern_tags = [tag for tag in self._tag_pattern.keys() if self._tag_pattern[tag].match(_p)]
        if len(pattern_tags) > 0:
            print pattern_tags, "-->", _p
            result['word_tag'][_p].extend(pattern_tags)

    def _read_unit_from_file(self, file_name):
        for line in open(file_name).readlines():
            line = line.strip().split(':')
            to_add = {l.strip() for l in line[1].split(' ')}
            self._word_tag_map[line[0].strip()] = self._word_tag_map[line[0].strip()].union(to_add)
            self._unit_set.add(line[0].strip())

    def _read_dict_from_pair(self, file_name):
        for line in open(file_name):
            if type(line) == unicode:
                line = line.encode('utf-8')
            # print line
            if line[0] != '#':
                tokens = line.strip().split(':')
                #print tokens
                if len(tokens) == 2:
                    self._word_tag_map[tokens[1].strip()].add(tokens[0].strip())

    def _read_dict_from_table(self, file_name):
        ret = dict()
        for line in open(file_name):
            line = line.strip().split('\t')
            if len(line) == 2:
                ret[self._normalizer.normalize_line(line[0])] = line[1]
            if len(line) > 2:
                ret[self._normalizer.normalize_line(line[0])] = line[1:]
        return ret

    def _form_regex_need_split(self, file_name, delimiter):
        lines = [line.strip().lower().split(delimiter) for line in open(file_name)
                 if line[0] != '#' and line.strip() != ""]
        words = []
        for line in lines:
            words.extend(line)
        words = [self._normalizer.tosingular(w) for w in words]
        return words
        # return re.compile('|'.join(words))

    def _read_dict(self, file_name):
        ret = set()
        for line in open(file_name):
            ret.add(self._normalizer.normalize_line(line))
            self._denormalize[self._normalizer.normalize_line(line)] = line.strip()
        return ret
        # return set([self._normalizer.normalize_line(line) for line in open(file_name)])

    def _denormalizer(self, word):
        if word in self._denormalize.keys():
            return self._denormalize[word]
        return word

    def batch_analysis(self, query_file):
        output_file = 'output.txt'
        w = open(output_file, 'wb')
        for line in open(query_file):
            w.write(json.dumps(self.analyze(line.strip())))
        w.close()
        html_download = '<a href=download_batch_queries_analysis_result> Query Analysis Result</a>'
        return '../../resources/Webpages/test.html'.format('batch', html_download)

    def analyze(self, phrase):
        if type(phrase) == unicode:
            phrase = phrase.encode('utf-8')
        result = dict()
        normalized_phrase = ' '.join([self._normalizer.tosingular(w) for w in phrase.split() if w.strip() != ""])
        normalized_phrase = normalized_phrase.replace('   ', ' ').replace('  ', ' ')
        result['original phrase'] = phrase
        result['normalized phrase'] = normalized_phrase
        result['word_tag'] = defaultdict(list)
        result['synonyms'] = defaultdict(set)
        #result['query categorization'] = 'TBD'
        result['key_word'] = 'TBD'
        result['key_word_id'] = 'TBD'
        result['not_search'] = list()
        result['product_type_id'] = list()
        result['brand_id'] = list()
        result['gender'] = set()
        result['quantity'] = match_quantity_and_unit(phrase.lower())
        #ordered_tag = list()
        words = [self._normalizer.tosingular(w) for w in normalized_phrase.split(' ')]
        hit = []
        location = defaultdict(set)
        possible_model = set()
        for l in range(5, 0, -1):
            cur_hit = []
            for i in range(len(words) - l + 1):
                if i not in hit:
                    p = ' '.join(words[i:i + l])
                    p = p.strip()
                    if p != "":
                        if p in self._synonym_map:
                            for syn_index in self._synonym_map[p]:
                                result['synonyms'][p].update(self._synonyms[syn_index])
                        assigned_tag = False
                        for rule in self._pre_pattern_list:
                            if rule.run(p) is not None:
                                part = rule.run(p)
                                for key, value in part:
                                    result['word_tag'][key].extend(value)
                                    normalized_phrase = normalized_phrase.replace(p, key)
                                for l2 in range(l):
                                    cur_hit.append(i + l2)
                                location[i] = p
                                continue
                        if p in self._gender_map:
                            result['gender'].add(self._gender_map[p])
                        if p in self._big_map:
                            for l2 in range(l):
                                cur_hit.append(i + l2)
                            location[i] = p
                            result['word_tag'][p] = list(self._big_map[p])
                            assigned_tag = True
                            '''
                            if p in self._brand_model.keys():
                                d = {l[0]:(l[1], l[2]) for l in possible_model}
                                common = self._brand_model[p].intersection(set(d.keys()))
                                if len(common) > 0:
                                    for k in common:
                                        result['word_tag'][k].append('series_model')
                                        for i in range(1, d[k][1]):
                                            if d[k][0] + 1 in location:
                                                result['word_tag'].pop(location[d[k][0] + i])
                                                location.pop(d[k][0] + i)
                            '''
                        if p in self._model_brand.keys() and (p not in result['word_tag'] or (p in result['word_tag'] and 'series_model' not in result['word_tag'][p])):
                                if len(set(self._model_brand[p]).intersection(set(result['word_tag'].keys()))) != 0:
                                    for l2 in range(l):
                                        cur_hit.append(i + l2)
                                    location[i] = p
                                    result['word_tag'][p].append('series_model')
                                    assigned_tag = True
                                # else:
                                #     possible_model.add((p, i, l))

                        if not result['word_tag'][p]:
                                result['word_tag'].pop(p)
                        if not assigned_tag:
                            for rule in self._pattern_list:
                                if rule.run(p) is not None:
                                    part = rule.run(p)
                                    for key, value in part:
                                        result['word_tag'][key].extend(value)
                                        normalized_phrase = normalized_phrase.replace(p, key)
                                    for l2 in range(l):
                                        cur_hit.append(i + l2)
                                    location[i] = p
                hit.extend(cur_hit)

        result['gender'] = ['male', 'female'] if len(result['gender']) == 0 else list(result['gender'])
        ordered_tag = [l[1] for l in sorted(location.items(), key=lambda x: x[0])]
        not_tagged = normalized_phrase
        tagged_words = result['word_tag'].keys()
        tagged_words.sort(key=len, reverse=True)

        for w in tagged_words:
            not_tagged = not_tagged.replace(w, '')

        for w in not_tagged.strip().split(' '):
            if w != '':
                result['word_tag'][w].append('untagged')

        #self._sort_dict(result, location, not_tagged.strip().split(' '), words)

        #result['query categorization'] = self._queryCategorizer.categorize(result)

        for k in result['synonyms'].keys():
            result['synonyms'][k].remove(k)
            result['synonyms'][k] = list(result['synonyms'][k])

        self._post_tag_result(result, ordered_tag)
        #return json.dumps(result)
        return result

    @staticmethod
    def _sort_dict(result, location, not_tagged, words):
        orderdict = OrderedDict()
        length = len(words)
        #length = len(not_tagged) + len(result['word_tag'])
        i = 0
        while i < length:
            if i not in location.keys():
                if len(not_tagged) == 0:
                    i += 1
                    continue
                curr = not_tagged.pop(0)
                i += 1
                while curr == '':
                    if len(not_tagged) == 0:
                        break
                    curr = not_tagged.pop(0)
                    i += 1
                orderdict[curr] = result['word_tag'][curr]
            else:
                orderdict[location[i]] = result['word_tag'][location[i]]
                i += len(location[i].split(' '))

        result['word_tag'] = orderdict

    @staticmethod
    def _replace(l, item1, item2):
        index = l.index(item1[0])
        l.remove(item1[0])
        l.insert(index, item2)

    def _post_product_process(self, product_list, ordered_tag, result):
        if len(product_list) == 0:
            return
        #product_list = \
        product_list.sort(key=lambda x: ordered_tag.index(x[0]))
        #sorted(product_list, key=lambda x: ordered_tag.index(x[0]))
        pre = product_list[0][0]
        i = 0
        length = len(product_list)
        #new_product = list()
        #for i in range(1, len(product_list)):

        while i < length:
            if pre.split(' ') > 1 and (pre.split(' ')[-1] + ' ' + product_list[i][0]) in self._word_tag_map['product']:
                first_word = ' '.join(pre.split(' ')[:-1])
                second_word = pre.split(' ')[-1] + ' ' + product_list[i][0]
                if first_word in self._word_tag_map['product']:
                    self._replace(ordered_tag, product_list[i - 1], first_word)
                    self._replace(ordered_tag, product_list[i], second_word)
                    temp1 = result['word_tag'][product_list[i - 1][0]]
                    result['word_tag'].pop(product_list[i - 1][0])
                    result['word_tag'][first_word] = temp1
                    temp2 = result['word_tag'][product_list[i][0]]
                    result['word_tag'].pop(product_list[i][0])
                    result['word_tag'][second_word] = temp2
                    first = (first_word, self._product_hierarchy[first_word.split(' ')[-1]])
                    second = (second_word, self._product_hierarchy[second_word.split(' ')[-1]])
                    product_list.pop(i - 1)
                    product_list.insert(i - 1, first)
                    product_list.pop(i)
                    product_list.insert(i, second)
                    pre = product_list[i][0]
                    i += 1
                    continue
                elif first_word in self._word_tag_map['demography']:
                    self._replace(ordered_tag, product_list[i - 1], first_word)
                    self._replace(ordered_tag, product_list[i], second_word)
                    #temp1 = result['word_tag'][product_list[i - 1]]
                    result['word_tag'].pop(product_list[i - 1][0])
                    result['word_tag'][first_word] = ['demography']
                    temp2 = result['word_tag'][product_list[i][0]]
                    result['word_tag'].pop(product_list[i][0])
                    result['word_tag'][second_word] = temp2
                    second = (second_word, self._product_hierarchy[second_word.split(' ')[-1]])
                    product_list.pop(i - 1)
                    product_list.pop(i - 1)
                    product_list.insert(i - 1, second)
                    pre = product_list[i - 1][0]
                    length -= 1
                    continue
            pre = product_list[i][0]
            i += 1

    def _post_tag_result(self, result, ordered_tag):
        product_list = list()
        brand_list = set()
        model_list = set()
        #key_word_list = [product_list, brand_list, model_list]
        l = [[], [], [], []]
        pre_key = None
        pre_value = None
        new_tag = OrderedDefaultDict()
        new_tag.default_factory = list
        for key, value in result['word_tag'].items():
            if len({'product'}.intersection(value)) != 0:
                product_list.append((key, self._product_hierarchy[key.split(' ')[-1]]))
            if 'brand' in value:
                result['word_tag'].pop(key)
                result['word_tag'][self._brand_mapping[key]].append('brand')
                try:
                    result['normalized phrase'] = result['normalized phrase'].replace(key, self._denormalizer(key))
                except:
                    pass
                key = self._brand_mapping[key]
                if key in self._type_id.keys():
                    result['brand_id'].append(self._type_id[key])
                brand_list.add(self._denormalizer(key))
            if 'store_name' in value:
                result['word_tag'].pop(key)
                result['word_tag'][self._store_mapping[key]].append('store_name')
                key = self._store_mapping[key]
            if 'series_model' in value:
                model_list.add(key)
            if pre_value is not None and set(value).intersection(self._unit_set) != set() and 'range' in pre_value:
                new_tag.pop(pre_key)
                new_tag[pre_key + ' ' + key].extend([value[0] + ' ' + pre_value[0]])
            else:
                if len(set(value).intersection({'brand', 'characters', 'store_name'})) != 0 and len(set(value).intersection({'product'})) == 0:
                    new_tag[self._denormalizer(key)].extend(value)
                else:
                    new_tag[key].extend(value)
            pre_key = key
            pre_value = value
        result['word_tag'] = new_tag
        #self._post_product_process(product_list, ordered_tag, result)

        for item in product_list:
            result['product_type_id'].append(self._type_id[item[0]])
            l[item[1]].append(item[0])
        #test of new way
        indexes = list()
        for word in self._seperate_word:
            if word in ordered_tag:
                indexes.append(ordered_tag.index(word))
        indexes.append(len(ordered_tag))
        indexes.sort()

        for index in indexes:
            candidate = list()
            for i in range((len(l) - 1), -1, -1):
                l[i] = sorted(l[i], key=lambda x: ordered_tag.index(x), reverse=True)
                for key in l[i]:
                    if ordered_tag.index(key) < index and key not in Key_word_exception:
                        result['key_word'] = key
                        try:
                            result['key_word_id'] = self._type_id[key]
                        except:
                            pass
                        return
                    elif ordered_tag.index(key) < index and key in Key_word_exception:
                        candidate.append(key)
            if len(candidate) > 0:
                result['key_word'] = candidate[0]
                try:
                    result['key_word_id'] = self._type_id[candidate[0]]
                except:
                    pass
                return

        #test of new way
        '''
        for i in range(len(l) - 1, -1, -1):
            l[i] = sorted(l[i], key=lambda x: ordered_tag.index(x), reverse=True)
            if len(l[i]) != 0:
                #result['key_word'] = self._type_id[l[i][0]]
                index = len(ordered_tag)
                for word in self._seperate_word:
                    if word in ordered_tag:
                        index = ordered_tag.index(word)
                if ordered_tag.index(l[i][-1]) > index:
                    index = len(ordered_tag)
                give_up = str()
                for key in l[i]:
                    give_up = key
                    if key in Key_word_exception:
                        continue
                    if ordered_tag.index(key) < index:
                        result['key_word'] = key
                        try:
                            result['key_word_id'] = self._type_id[key]
                        except:
                            pass
                        return
                    elif index != len(ordered_tag) and len(product_list) > 1 and ordered_tag.index(l[i][-1]) < index:
                        continue
                    elif result['key_word'] == 'TBD':
                        result['key_word'] = l[i][0]
                        try:
                            result['key_word_id'] = self._type_id[l[i][0]]
                        except:
                            pass
                #result['not_search'] = self._not_search[result['key_word']]
                        return
                if result['key_word'] == 'TBD':
                    result['key_word'] = give_up
                    try:
                        result['key_word_id'] = self._type_id[give_up]
                    except:
                        pass
        '''
        # if len(brand_list) != 0:
        #     result['key_word'] = brand_list.pop()
        #     #result['not_search'] = self._not_search[result['key_word']]
        #     return
        # elif len(model_list) != 0:
        #     result['key_word'] = model_list.pop()
        #     #result['not_search'] = self._not_search[result['key_word']]



if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.analyze('Bedtime Originals Magic Kingdom Wall DÃ©cor	Bedtime Originals Pinkie Wall DÃ©cor	')
    #print analyzer.analyze("shoes", 0)
    '''
    produc_list = {l.lower().strip() for l in  open("../resource/table/products.txt").readlines()}
    ans_dict = dict()
    for p in produc_list:
        ans_dict[p] = analyzer.analyze(p)
    open("../resource/table/product_type_cache.json", "wb").write(json.dumps(ans_dict, cls=SetEncoder))
    ""
    count = 0
    '''
    '''
    for q in open(Analyzer.QUERY_DIR + "relevant_queries.txt"):
        count += 1
        analyzer.analyze(q, count)
    '''