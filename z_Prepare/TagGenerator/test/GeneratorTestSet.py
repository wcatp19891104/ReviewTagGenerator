__author__ = 'wangzaicheng'


JJ_FILE = "./record_of_JJ.txt"
TYPE_FILE = "./record_of_type.txt"
TAG_FILE = "./record_of_tag.txt"


import simplejson
import collections


data_jj = simplejson.loads(open(JJ_FILE).read().lower())
data_type = simplejson.loads(open(TYPE_FILE).read().lower())
data_tag = simplejson.loads(open(TYPE_FILE).read().lower())

ALL_REVIEW_FILE = "all_record.txt"


def generate_test_set(ratio=0.7):
    data = simplejson.loads(open(ALL_REVIEW_FILE).read().lower())
    test_data = collections.defaultdict(dict)
    length = len(data) * ratio
    count = 0
    print len(data)
    useful = 0
    for review_name in data:
        count += 1
        #if count > length:
        #    break
        if "tag" in data[review_name] and "type" in data[review_name] and "jj" in data[review_name]:
            useful += 1
            # list
            tag = data[review_name]["tag"]
            # list
            jj = data[review_name]["jj"]
            # string
            type = data[review_name]["type"]
            if len(tag) != 0 and len(jj) != 0 and type != "" and type != "tbd":
                test_data[review_name]["tag"] = tag
                test_data[review_name]["jj"] = jj
                test_data[review_name]["type"] = type
    print len(test_data)
    print useful
    # w = open("TestSet.txt", "w")
    # w.write(simplejson.dumps(test_data))
    # w.close()


if __name__ == "__main__":
    generate_test_set()
