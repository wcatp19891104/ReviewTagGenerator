__author__ = 'wangzaicheng'


import nltk
import codecs


UDT_TAG_FILE = "../dictionary/UDF_Tagger.txt"


class MyTagger:
    def __init__(self):
        self.default_tagger = nltk.data.load(nltk.tag._POS_TAGGER)
        model = {l.strip().split('\t')[0]: l.strip().split('\t')[1] for l in codecs.open(UDT_TAG_FILE, encoding='utf-8').readlines() if l.strip()[0] != '#'}
        self.tagger = nltk.tag.UnigramTagger(model=model, backoff=self.default_tagger)

    def tag(self, tokens):
        return self.tagger.tag(tokens)


if __name__ == "__main__":
    mytagger = MyTagger()
    print mytagger.tag(['.6'])