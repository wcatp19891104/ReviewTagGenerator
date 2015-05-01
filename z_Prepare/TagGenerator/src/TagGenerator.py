__author__ = 'wangzaicheng'
#TODO 1, regard review title more important; # 2, regard bottom line as overall motion


P_TAG = "../resource/P_tag.txt"
P_TAG_JJ = "../resource/P_tag_jj.txt"
P_TYPE_TAG = "../resource/P_type_tag.txt"
TEST_FILE = "../test/TestSet.txt"


import simplejson
import codecs


class Predictor:
    def __init__(self):
        self.p_tag = simplejson.loads(codecs.open(P_TAG).readline().lower())
        self.p_tag_jj = simplejson.loads(codecs.open(P_TAG_JJ).readline().lower())
        self.p_type_tag = simplejson.loads(codecs.open(P_TYPE_TAG).read().lower())

    def predict(self, words, type):
        result_board = dict()
        tags = self.p_tag.keys()
        for tag in tags:
            curr_prob = 1.0
            curr_w = 1.0
            for word in words:
                try:
                    curr = float(self.p_tag_jj[tag][word]) * float(self.p_type_tag[type][tag])
                    if curr != 0.0:
                        curr_prob *= curr
                except:
                    pass
            if curr_prob == 1:
                curr_prob = 0
            result_board[tag] = curr_prob
        print sorted(result_board.items(), key=lambda x: x[1], reverse=True)[0: 10]


if __name__ == "__main__":
    p = Predictor()
    p.predict([u'wide', u'safe', u'back', u'discovered', u'simply', u'nearly', u'grateful', u'still', u'open', u'again', u'unfortunately', u'later', u'together', u'found', u'soft', u'plush'], 'diaper')
    p.predict([], 'diaper')
