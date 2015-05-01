__author__ = 'wangzaicheng'


import codecs
import collections
import sys
import os
import json

import matplotlib
matplotlib.use('TkAgg')
import pylab
import matplotlib.pyplot as plt
from numpy import diff


SOURCE_FILE = "../resource/all_review.txt"
FREQUENCY_FILE = "../resource/pro.txt"
COVERAGE_RESULT_FILE = "../dictionary/tag_coverage_above_{0}.txt"
RECORD_FILE = "../resource/record_of_tag.txt"
TAG_REVIEW_FILE = "../resource/babiesrus_review.txt"


class Tag_Finder():
    def __init__(self):
        self.review_tags = dict()
        self._read_file()

    def _read_file(self):
        data = open(TAG_REVIEW_FILE).readlines()
        for entry in data:
            entry = json.loads(entry)
            curr_tag = [l.lower() for l in entry['pros']]
            curr_review = entry['review_text'][-1].lower()
            self.review_tags[curr_review] = curr_tag

    def process_single(self, review):
        if review in self.review_tags:
            return self.review_tags[review], []
        return [], []


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class CoverDetector:
    def __init__(self, force=False):
        self.cleaner = Tag_Finder()
        self.instances = {l.strip().lower() for l in codecs.open(SOURCE_FILE, encoding='utf-8').readlines()}
        self.frequency = [l.strip().lower().split('\t')[0] for l in codecs.open(FREQUENCY_FILE, encoding='utf-8').readlines()]
        self.instance_coverage = set()
        self.instance_tags = collections.defaultdict(set)
        self.reverse_instance_tags = collections.defaultdict(set)
        self._initialize_tags(force)

    def _coverage_monitor(self):
        return len(self.instance_coverage) / float(len(self.instances))

    def _initialize_tags(self, force=False):
        """
        generate two dict:
        1. jj to review
        2. review to jj, this is used to calculate number of occurs of JJ in review

        """
        if not os.path.exists(RECORD_FILE) or force:
            count = 0
            for review in self.instances:
                print count
                count += 1
                tags = set(self.cleaner.process_single(review)[0])
                self.instance_tags[review] = set(tags)
                for tag in tags:
                    self.reverse_instance_tags[tag].add(review)
            open(RECORD_FILE, 'wb').write(json.dumps(self.instance_tags, cls=SetEncoder))
        else:
            self.instance_tags = json.loads(open(RECORD_FILE).read())
            for instance in self.instance_tags:
                self.instance_tags[instance] = set(self.instance_tags[instance])
            for review in self.instance_tags:
                tags = self.instance_tags[review]
                for tag in tags:
                    self.reverse_instance_tags[tag].add(review)
            print "data loaded"

    def generator(self):
        """
        iterator of jj
        :param key: jj
        """
        for jj in self.frequency.keys():
            yield jj

    def process(self, threshold=0.9, coverage_threshold=3):
        """
        write file of new coverage of jj
        :param threshold:
        :param coverage_threshold:
        """
        key = str()
        jj_list = list()
        y = []
        for key in self.frequency:
            print key
            jj_list.append(key)
            for review in self.reverse_instance_tags[key]:
                self.instance_tags[review].add(key)
                if len(self.instance_tags[review]) >= coverage_threshold:
                    self.instance_coverage.add(review)
            print self._coverage_monitor()
            y.append(self._coverage_monitor())
            if self._coverage_monitor() >= threshold:
                break
        print len(jj_list)
        w = open(COVERAGE_RESULT_FILE.format(str(threshold)), "wb")
        for jj in jj_list:
            try:
                w.write(jj + '\n')
            except:
                print "special char! ", jj
        w.close()
        x = pylab.arange(1, len(y) + 1, 1)
        plt.plot(x, y)
        plt.show()

        dx = 1
        dy = diff(y) / dx
        y_dict = dict()
        for i in range(len(dy)):
            y_dict[i] = dy[i]

        sorted_diff = sorted(y_dict.items(), key=lambda x: x[1], reverse=True)
        sorted_diff = [l for l in sorted_diff if l[0] > 100]
        print sorted_diff[0: 10]

        x = pylab.arange(1, len(y), 1)
        plt.plot(x, dy)
        plt.show()


if __name__ == "__main__":
    cover = CoverDetector()
    cover.process(threshold=0.71, coverage_threshold=1)

