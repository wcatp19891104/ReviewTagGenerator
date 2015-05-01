# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import os.path
import codecs
import simplejson
import TagClean
import collections
import KeywordFinder


Train_Data_File = "../resource/babiesrus_review.txt"
Bayes_Model_File_Tag = "../Model/P_tag.txt"
Bayes_Model_File_JJ = "../Model/P_tag_jj.txt"
Bayes_Model_Category = "../Model/Bayes_Model_Category.txt"
Proto_File = "../util/babiesrus_proto.txt"
Valid_Con_Tag = "../resource/validate_60_con.txt"
Valid_Pro_Tag = "../resource/validate_80_pro.txt"
P_JJ_In_Category = "../Model/p_of_JJ_in_category.txt"
P_Tag_In_Category = "../Model/p_of_tag_in_category.txt"
P_Tag_In_Type = "../Model/P_type_tag.txt"



class BayesMode:
    def __init__(self, force=False):
        self.keyword_finder = KeywordFinder.KeyWordFinder()
        self.cleaner = TagClean.TagClean()
        self.valid_con = [l.strip().lower() for l in codecs.open(Valid_Con_Tag, encoding='utf-8').readlines()]
        self.valid_pro = [l.strip().lower() for l in codecs.open(Valid_Pro_Tag, encoding='utf-8').readlines()]
        self.p_tag_con = dict()
        self.p_tag_pro = dict()
        self.p_jj_in_tag_con = dict()
        self.p_jj_in_tag_pro = dict()
        self.p_category = dict()
        self.p_jj_in_category = dict()
        self.p_tag_in_category = dict()
        self.p_tag_in_type = dict()
        self.load(force)
        pass

    def load(self, force=False):
        #all_tag = ReviewTag_pb2.AllTag()
        con_tag = collections.defaultdict(collections.Counter)
        pro_tag = collections.defaultdict(collections.Counter)
        con_tag_counter = collections.Counter()
        pro_tag_counter = collections.Counter()
        if not os.path.isfile(Bayes_Model_File_Tag) or force:
            data = codecs.open(Train_Data_File, encoding='utf-8').readlines()
            count = 0
            for line in data:
                print count
                count += 1
                curr_data = simplejson.loads(line.lower())
                curr_review = curr_data['review_text'][-1]
                curr_jj = self.cleaner.process_single(curr_review)[0]
                for tag in curr_data['cons']:
                    if tag.lower() not in self.valid_con:
                        continue
                    con_tag_counter[tag] += 1
                    for j in curr_jj:
                        con_tag[tag][j] += 1
                for tag in curr_data['pros']:
                    if tag.lower() not in self.valid_pro:
                        continue
                    pro_tag_counter[tag] += 1
                    for j in curr_jj:
                        pro_tag[tag][j] += 1
            p_tag_con = dict()
            p_tag_pro = dict()
            p_jj_in_tag_con = collections.defaultdict(dict)
            p_jj_in_tag_pro = collections.defaultdict(dict)
            tag_con_sum = sum(con_tag_counter.values())
            tag_pro_sum = sum(pro_tag_counter.values())
            for item in con_tag_counter.items():
                p_tag_con[item[0]] = item[1] / float(tag_con_sum)
            for item in pro_tag_counter.items():
                p_tag_pro[item[0]] = item[1] / float(tag_pro_sum)
            for item in con_tag.items():
                curr_jj_sum = sum(item[1].values())
                for jj in item[1]:
                    p_jj_in_tag_con[item[0]][jj] = item[1][jj] / float(curr_jj_sum)
            for item in pro_tag.items():
                curr_jj_sum = sum(item[1].values())
                for jj in item[1]:
                    p_jj_in_tag_pro[item[0]][jj] = item[1][jj] / float(curr_jj_sum)
            w_1 = open(Bayes_Model_File_Tag, 'wb')
            w_2 = open(Bayes_Model_File_JJ, 'wb')
            w_1.write(simplejson.dumps(p_tag_pro) + '\n')
            w_1.write(simplejson.dumps(p_tag_con))
            w_2.write(simplejson.dumps(p_jj_in_tag_pro) + '\n')
            w_2.write(simplejson.dumps(p_jj_in_tag_con))
            #TODO add training for tag, type
            print "trained"
        else:
            with open(Bayes_Model_File_Tag) as r:
                lines = r.readlines()
                self.p_tag_pro = simplejson.loads(lines[0])
                self.p_tag_con = simplejson.loads(lines[1])
            with open(Bayes_Model_File_JJ) as r:
                lines = r.readlines()
                self.p_jj_in_tag_pro = simplejson.loads(lines[0])
                self.p_jj_in_tag_con = simplejson.loads(lines[1])
            with codecs.open(Bayes_Model_Category) as r:
                self.p_category = simplejson.loads(r.read())
            with codecs.open(P_JJ_In_Category) as r:
                self.p_jj_in_category = simplejson.loads(r.read())
            with codecs.open(P_Tag_In_Category) as r:
                self.p_tag_in_category = simplejson.loads(r.read())
            with codecs.open(P_Tag_In_Type) as r:
                self.p_tag_in_type = simplejson.loads(r.read())
            print "loaded"

    def get_tags(self, string):
        return self.keyword_finder.get_tags(string)

    def process_with_type(self, string, product_type):
        jjs = self.cleaner.process_single(string)[0]
        score_board_pro = collections.defaultdict(lambda: 0.0)
        score_board_con = collections.defaultdict(lambda: 0.0)

    def process(self, string, product_type):
        jjs = self.cleaner.process_single(string)[0]
        print jjs
        score_board_pro = collections.defaultdict(lambda: 0.0)
        score_board_con = collections.defaultdict(lambda: 0.0)
        for jj in jjs:
            for tag in self.p_tag_con:
                try:
                    score_board_con[tag] += self.p_tag_con[tag] * self.p_jj_in_tag_con[tag][jj]
                except:
                    pass
            for tag in self.p_tag_pro:
                try:
                    score_board_pro[tag] += self.p_tag_pro[tag] * self.p_jj_in_tag_pro[tag][jj]
                except:
                    pass
        score_board_pro = sorted(score_board_pro.items(), key=lambda x: x[1], reverse=True)
        score_board_con = sorted(score_board_con.items(), key=lambda x: x[1], reverse=True)
        #valid_tags = set(self.keyword_finder.get_tags(product_type))
        valid_tags = [l[0] for l in sorted(self.keyword_finder.get_tags(product_type), key=lambda x: x[1], reverse=True)[0:5]]
        ret_pro = list()
        ret_con = list()
        for tag in score_board_pro:
            if tag[0] in valid_tags:
                ret_pro.append(tag)
        for tag in score_board_con:
            if tag[0] in valid_tags:
                ret_con.append(tag)
        print ret_con
        print ret_pro
        print "max pro: ", score_board_pro[0: 10]
        print "max con: ", score_board_con[0: 10]

    def process_in_category(self, string, product_type):
        jjs = self.cleaner.process_single(string)[0]
        print jjs
        score_board_con = collections.defaultdict(lambda: 0.0)
        score_board_pro = collections.defaultdict(lambda: 0.0)
        for jj in jjs:
            for cat in self.p_category:
                try:
                    score_board_pro[cat] += self.p_category[cat] + self.p_jj_in_category[cat][jj]
                except Exception:
                    pass
        #score_board_pro = sorted(score_board_pro.items(), key=lambda x: x[1], reverse=True)
        score_in_category = dict()
        for cat in score_board_pro:
            p_current = collections.defaultdict(lambda: 0.0)
            for jj in jjs:
                for tag in self.p_tag_in_category[cat]:
                    #if tag in self.keyword_finder.get_tags(product_type):
                        try:
                            p_current[tag] += self.p_tag_in_category[cat][tag] * float(self.p_jj_in_tag_pro[tag][jj])
                        except Exception:
                            pass
            score_in_category[cat] = p_current
        for k in score_in_category:
            score_in_category[k] = dict(sorted(score_in_category[k].items(), key=lambda x: x[1], reverse=True)[0:10])
            print k, score_in_category[k]

        final_board = collections.defaultdict(lambda: 0.0)
        for cat in score_in_category:
            for tag in score_in_category[cat]:
                final_board[tag] = score_in_category[cat][tag] * score_board_pro[cat]

        final_board = sorted(final_board.items(), key=lambda x: x[1], reverse=True)[0: 10]
        print "max category: ", final_board

    def p_tag_type(self, tag, type):
        try:
            return self.p_tag_in_type[type][tag]
        except Exception:
            return 0




if __name__ == "__main__":
    model = BayesMode()
    #model.process(open('test.txt').read(), "crib")
    model.process_in_category(open('test.txt').read(), "diaper")
    #print model.get_tags('diaper')
    pass
