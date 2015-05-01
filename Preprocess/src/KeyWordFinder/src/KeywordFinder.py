__author__ = 'wangzaicheng'
"""
keyword finder:
1. generate key word -> tag mapping and p_tag_type
2. find tags given key word: get_tags(keyword)
3. record review to key word mapping and title key word mapping: generate_record_of_key_word(review)
4. find keyword given review: get_keyword(review)
5. fill review field of keyword

"""
import os
import collections
import codecs
import sys

import simplejson


CURR_DICT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, CURR_DICT + "/../../")

from backend_api.src.API import analyzer_api
from Review import Review

#key word to tag
Keyword_Back_File = CURR_DICT + "/../resource/keyword_back.txt"

#review, type
record_of_key_word = CURR_DICT + "/../resource/record_of_type.txt"

#title, type
record_of_title_type = CURR_DICT + "/../resource/record_of_title_type.txt"

#training data
Train_Data_File = CURR_DICT + "/../resource/babiesrus_review_title.txt"

#p of tag, type
P_Of_Tag_In_Type = CURR_DICT + "/../resource/P_type_tag.txt"


class KeyWordFinder:
    def __init__(self, force=False):
        self.keyword2tag = dict()
        self.review2keyword = dict()
        self.title2keyword = dict()
        self.query_engine = analyzer_api.Analyzer_API()
        self.load(force)
        pass

    def load(self, force=False):
        if not os.path.isfile(Keyword_Back_File) or force:
            keyword2tag = collections.defaultdict(collections.Counter)
            with codecs.open(Train_Data_File, encoding='utf-8') as r:
                data_set = r.readlines()
            count = 0
            print len(data_set)
            for data in data_set:
                print count
                count += 1
                data = simplejson.loads(data.lower())
                curr_id = data['product_id']
                try:
                    #solr_data = requests.get(solr_url.format(curr_id)).text
                    #solr_data = simplejson.loads(solr_data)['response']['docs'][0]
                    curr_title = data['title'][0]
                    #query_data = requests.get(queryunderstanding_url.format(urllib.quote(curr_title))).text
                    query_data = self.query_engine.to_solr(curr_title)
                    curr_keyword = query_data['key_words']
                except:
                    print "no title/keyword found with ", curr_id
                    continue
                for entry in data['cons']:
                    keyword2tag[curr_keyword][entry] += 1
                for entry in data['pros']:
                    keyword2tag[curr_keyword][entry] += 1
                #keyword2tag[curr_keyword][data['pros']] += 1
                #keyword2tag[curr_keyword] = list(set(keyword2tag[curr_keyword]))
            self.keyword2tag = keyword2tag
            with open(Keyword_Back_File, "wb") as w:
                w.write(simplejson.dumps(keyword2tag))
            print "trained key word to tag"
        if not os.path.isfile(record_of_key_word) or not os.path.isfile(record_of_title_type) or force:
            self.generate_record_of_key_word()
            with open(record_of_key_word) as r:
                self.review2keyword = simplejson.loads(r.read())
            print "trained review to key word"
        else:
            with open(Keyword_Back_File) as r:
                self.keyword2tag = simplejson.loads(r.read())
            with open(record_of_key_word) as r:
                self.review2keyword = simplejson.loads(r.read())
            with open(record_of_title_type) as r:
                self.title2keyword = simplejson.loads(r.read())
            print "loaded"

    def p_of_tag_in_type(self):
        with codecs.open(Keyword_Back_File, encoding='utf-8') as r:
            p_tag_type = collections.defaultdict(dict)
            data = simplejson.loads(r.read())
            for key in data:
                curr_sum = sum([int(l[1]) for l in data[key].items()])
                for tag in data[key]:
                    p_tag_type[key][tag] = int(data[key][tag]) / float(curr_sum)
        w = open(P_Of_Tag_In_Type, 'w')
        w.write(simplejson.dumps(p_tag_type))
        w.close()

    def generate_record_of_key_word(self):
        with codecs.open(Train_Data_File, encoding="utf-8") as r:
            record_data = dict()
            title_dict = dict()
            data_set = r.readlines()
            print len(data_set)
            count = 0
            for data in data_set:
                data = simplejson.loads(data.lower())
                try:
                    curr_title = data['title'][0].lower()
                    query_data = self.query_engine.to_solr(curr_title)
                    curr_keyword = query_data['key_words']
                    curr_review = data['review_text'][-1].lower()
                    # curr_id = data['product_id']
                    # solr_data = requests.get(solr_url.format(curr_id)).text
                    # solr_data = simplejson.loads(solr_data)['response']['docs'][0]
                    # curr_title = solr_data['title']
                    # query_data = self.query_engine.to_solr(curr_title)
                    # curr_keyword = query_data['key_words']
                    print count
                    count += 1
                except:
                    print "error in key word"
                    continue
                record_data[curr_review] = curr_keyword
                title_dict[curr_title] = curr_keyword
        with open(record_of_key_word, "w") as w:
            w.write(simplejson.dumps(record_data))
        with open(record_of_title_type, "w") as w:
            w.write(simplejson.dumps(title_dict))

    def get_tags(self, keyword):
        '''
        get tag given keyword
        :param keyword:
        :return: a list of tag
        '''
        if keyword in self.keyword2tag:
            return self.keyword2tag[keyword]
        return []

    def get_keyword(self, review):
        '''
        get key word from a review content
        :param review:
        :return: a str of key word
        '''
        if isinstance(review, str):
            if review.lower() in self.review2keyword:
                return self.review2keyword[review.lower()]
            return ""
        if isinstance(review, Review):
            if review.content.lower() in self.review2keyword:
                return self.review2keyword[review.content.lower()]
            return ""
        return ""

    def fill_review(self, review):
        '''
        fill review with key word and tag
        :param review:
        :return:
        '''
        if not isinstance(review, Review):
            print "not a Review Type"
        else:
            title = review.title
            if title.lower() in self.title2keyword:
                review.type = self.title2keyword[title.lower()]
            else:
                curr_type = self.query_engine.to_solr(title)['key_words']
                if curr_type not in {"", " ", "TBD", "tbd"}:
                    review.type = curr_type


if __name__ == "__main__":
    #concrete()
    k = KeyWordFinder()
    #k.generate_record_of_key_word()
    #k.p_of_tag_in_type()
    print k.get_tags("diaper")
    pass


