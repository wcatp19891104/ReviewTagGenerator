__author__ = 'wangzaicheng'


import codecs
import collections
import json
import simplejson


CategoryFile = "./category_of_tags.txt"
CountOfWordFilePro = "./pro.txt"
CountOfWordFileCon = "./con.txt"
Bayes_Model_Category = "../Model/Bayes_Model_Category.txt"
P_Tag_In_Category_File = "../Model/p_of_tag_in_category.txt"
P_JJ_In_Category_File = "../Model/p_of_JJ_In_Category.txt"
P_JJ_In_Tag_File = "../Model/P_tag_jj.txt"


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def JsonUtil(JsonFile):
    data = json.loads(open(JsonFile).read())
    print data
    return data


def GenerateCategory():
    """
    category known tag into 8 categories, most 300, by programmer's hand

    """
    with codecs.open("CategroyOfWord.txt", "r", encoding="utf-8") as r:
        data = r.read().lower()
        data = data.split('\n')
        record = collections.defaultdict(set)
        for line in data[0: 101]:
            line = line.strip().split(':')
            category = line[0]
            for item in line[1].split('\t'):
                record[category.lower()].add(item.lower())
        number_key = dict()
        count = 1
        choose_string = str()
        for key in record.keys():
            choose_string += str(count) + '\t' + key + '\n'
            number_key[count] = key
            count += 1
    with codecs.open("validate_90_pro.txt", "r", encoding="utf-8") as r:
        data = r.read().lower().split('\n')
        for line in data[100: 300]:
            print '\n' * 10
            print choose_string
            try:
                input = raw_input(line + ": ")
                record[number_key[int(input)]].add(line)
            except:
                input = raw_input(line + ": ")
                record[number_key[int(input)]].add(line)
    w = open('category_of_tags.txt', 'wb')
    w.write(json.dumps(record, cls=SetEncoder))


def GeneratePOfCategory():
    """
    We should know p(category|JJ), so use this function generate P(category).
    the times of category are from times of it's tag. Tag count from 'pro.txt'
    or 'con.txt'

    """
    count = collections.defaultdict(int)
    with codecs.open(CountOfWordFilePro, encoding='utf-8') as r:
        for line in r.readlines():
            line = line.lower().strip().split('\t')
            count[line[0]] += int(line[1])
    total_count = sum(count.values())
    count_of_category = collections.defaultdict(int)
    with codecs.open(CategoryFile, encoding="utf-8") as r:
        category_dict = json.loads(r.read())
        for key in category_dict:
            for cat in category_dict[key]:
                count_of_category[key] += count[cat]
    P_category = collections.defaultdict(float)
    for key in count_of_category:
        P_category[key] = count_of_category[key] / float(total_count)
    w = open(Bayes_Model_Category, 'wb')
    w.write(json.dumps(P_category))
    print "finish generate Bayes Model for category P(Category)"


def GeneratePOfTagInCategory():
    """
    P(JJ|category) = sum(P(Tag|category) * P(JJ|tag)), P(JJ|tag) is known
    from ../Model/P_tag_jj.txt
    This function can calculate P(Tag|Category), tag only occurs in one category
    File Need: CategoryFile and CountOfWordFilePro

    """
    p_tag_category = collections.defaultdict(dict)
    count = collections.defaultdict(int)
    with codecs.open(CountOfWordFilePro, encoding='utf-8') as r:
        for line in r.readlines():
            line = line.lower().strip().split('\t')
            count[line[0]] += int(line[1])
    count_of_category = collections.defaultdict(int)
    with codecs.open(CategoryFile, encoding="utf-8") as r:
        category_dict = json.loads(r.read())
        for key in category_dict:
            for cat in category_dict[key]:
                count_of_category[key] += count[cat]
    for cat in category_dict:
        for tag in category_dict[cat]:
            p_tag_category[cat][tag] = count[tag] / float(count_of_category[cat])
    w = open(P_Tag_In_Category_File, 'wb')
    w.write(json.dumps(p_tag_category))


def GeneratePOfJJInCategory():
    """
    Calculate P(JJ|Category), with known of P(Tag|Category) * P(JJ|tag),
    P(Tag|Category) comes from P_Tag_In_Category_File,
    P(JJ|tag) come from ../Model/P_tag_jj.txt
    P_tag_jj.txt: two lines, pro + \n + con
    """
    p_jj_in_category = collections.defaultdict(dict)
    with codecs.open(P_JJ_In_Tag_File, encoding='utf-8') as r:
        p_jj_in_tag = simplejson.loads(r.read().lower().split('\n')[0])
    with codecs.open(P_Tag_In_Category_File, encoding='utf-8') as r:
        p_tag_in_category = json.loads(r.read())
    for tag in p_jj_in_tag:
        for jj in p_jj_in_tag[tag]:
            for cat in p_tag_in_category:
                if tag in p_tag_in_category[cat]:
                    p_jj_in_category[cat][jj] = p_jj_in_tag[tag][jj] * float(p_tag_in_category[cat][tag])
    w = open(P_JJ_In_Category_File, 'wb')
    w.write(json.dumps(p_jj_in_category))


def main():
    GeneratePOfCategory()
    GeneratePOfTagInCategory()
    GeneratePOfJJInCategory()

if __name__ == "__main__":
    main()
    #GenerateCategory()
    #GeneratePOfCategory()
    #curr = JsonUtil(Bayes_Model_Category)
    #GeneratePOfTagInCategory()
    #curr = JsonUtil(P_Tag_In_Category_File)
