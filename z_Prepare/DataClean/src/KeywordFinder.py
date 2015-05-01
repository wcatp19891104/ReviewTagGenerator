__author__ = 'wangzaicheng'

import os
import collections
import urllib
import codecs

import requests
import simplejson

from Prepare.DataClean.src.backend_api.src.API import analyzer_api


solr_url = 'http://192.168.2.12:8085/solr/collection1/select?q=*:*&fq=product_id_composite:%22babiesrus:{0}%22&wt=json'
queryunderstanding_url = 'http://192.168.2.12:8082/index?query={0}'
Keyword_Back_File = "../resource/keyword_back.txt"
record_of_key_word = "../resource/record_of_type.txt"
record_of_JJ = "../resource/record_of_JJ.txt"
record_of_tag = "../resource/record_of_tag.txt"
#Train_Data_File = "../resource/babiesrus_review.txt"
Train_Data_File = "../resource/babiesrus_review_title.txt"
P_Of_Tag_In_Type = "../resource/P_type_tag.txt"


class KeyWordFinder:
    def __init__(self, force=False):
        self.keyword2tag = dict()
        self.load(force)
        self.query_engine = analyzer_api.Analyzer_API()
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
                    query_data = requests.get(queryunderstanding_url.format(urllib.quote(curr_title))).text
                    curr_keyword = simplejson.loads(query_data)['key_words']
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
            print "trained"
        else:
            with open(Keyword_Back_File) as r:
                self.keyword2tag = simplejson.loads(r.read())
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
            data_set = r.readlines()
            print len(data_set)
            count = 0
            for data in data_set:
                data = simplejson.loads(data.lower())
                try:
                    curr_title = data['title'][0]
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
        w = open(record_of_key_word, "w")
        w.write(simplejson.dumps(record_data))

    def get_tags(self, string):
        try:
            query_data = requests.get(queryunderstanding_url.format(urllib.quote(string))).text
            query_data = simplejson.loads(query_data)
            key_word = query_data['key_words']
            ret = self.keyword2tag[key_word] if key_word in self.keyword2tag else []
            return ret
        except:
            return []


def concrete():
    data = collections.defaultdict(dict)
    tag_dict = simplejson.loads((open(record_of_tag).read().lower()))
    print len(tag_dict)
    jj_dict = simplejson.loads(open(record_of_JJ).read().lower())
    print len(jj_dict)
    type_dict = simplejson.loads(open(record_of_key_word).read().lower())
    print len(type_dict)
    count = 0
    for review in tag_dict:
        try:
            data[review]['tag'] = tag_dict[review]
            data[review]['jj'] = jj_dict[review]
            data[review]['type'] = type_dict[review]
            print count
            count += 1
        except:
            pass
    w = open("../resource/all_record.txt", "w")
    w.write(simplejson.dumps(data))
    w.close()


if __name__ == "__main__":
    concrete()
    #k = KeyWordFinder()
    #k.generate_record_of_key_word()
    #k.p_of_tag_in_type()
    #print k.get_tags("diaper")
    pass


