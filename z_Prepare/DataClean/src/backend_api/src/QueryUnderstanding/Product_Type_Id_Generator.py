__author__ = 'wangzaicheng'
# -*- coding: utf-8 -*-

import uuid
import random
import os

from src.QueryUnderstanding import plur2sing


ABS_PATH = os.path.dirname(os.path.realpath(__file__))
#product_id_mapping = '/'.join(ABS_PATH.split('/')[: -1]) + '/resource/table/product_id_mapping.txt'
product_id_mapping = ABS_PATH + '/../../resource/table/product_id_mapping.txt'
#product_list_file = '/'.join(ABS_PATH.split('/')[: -1]) + '/resource/table/products_backup.txt'
product_list_file = ABS_PATH + '/../../resource/table/products_backup.txt'


class ID_generator():
    def __init__(self):
        self.normalizer = plur2sing.Plur2Sing()
        self.id_dict = dict()
        self.product_list = set()
        for line in open(product_id_mapping).readlines():
            line = line.strip().split('\t')
            if len(line) > 1:
                self.id_dict[line[1]] = line[0]
        #for line in open(product_list_file).readlines():
        #    self.product_list.add(line.strip())
        self.product_list = set(self.id_dict.values())
        self.i = 0

    def add(self, word):
        changed = False
        if word not in self.product_list:
            changed = True
            id = hash(uuid.uuid3(uuid.NAMESPACE_OID, word)) % 1000000
            while str(id) in self.id_dict.keys():
                id = id + random.randint(1, 100)
            self.id_dict[str(id)] = word
            self.product_list.add(word)
            #print self.i
            self.i += 1
        return changed

    def refresh(self):
        changed = False
        for line in open(ABS_PATH + '/../../resource/table/new_products.txt').readlines():
            change = self.add(self.normalizer.normalize_line(line.strip()))
            if change:
                changed = True
        if changed:
            self.merge()

    def merge(self):
        w = open(product_id_mapping, 'wb')
        for item in self.id_dict.items():
            try:
                w.write(item[1] + '\t' + item[0] + '\n')
            except:
                print item[1]
        w.close()
        w = open(product_list_file, 'wb')
        for item in self.product_list:
            w.write(item + '\n')

    def clean_product(self):
        product_set = set()
        for line in open(product_list_file).readlines():
            line = self.normalizer.normalize_line(line.strip())
            product_set.add(line)
        w = open(product_list_file, 'wb')
        for item in product_set:
            w.write(item + '\n')
        w.close()


def list_clean(filename):
    normalizer = plur2sing.Plur2Sing()
    item_set = set()
    for line in open(filename).readlines():
        line = normalizer.normalize_line(line.strip())
        item_set.add(line)
    w = open('normalized_' + filename, 'wb')
    for item in item_set:
        w.write(item + '\n')
    w.close()


if __name__ == "__main__":
    g = ID_generator()
    #g.clean_product()

    #for line in open('products.txt').readlines():
    #    print line
    #    g.add(line.strip())
    # for line in open(product_list_file).readlines():
    #     g.add(line.strip())
    # g.merge()
    g.add('sleeve')
    g.merge()
