__author__ = 'wangzaicheng'


import nltk
import collections
import threading
import codecs
import sys

sys.path.append('../src/')

import TagClean


Review_File = "../resource/all_review.txt"


def pre_process_review(string, send_detector, useful_field=None):
    if not useful_field:
        useful_field = {l.strip() for l in codecs.open("../dictionary/emotion_list").readlines()}
    sends = send_detector.tokenize(string)
    ret = list()
    for send in sends:
        #print '-->', send
        tokens = nltk.word_tokenize(send.lower())
        tags = nltk.tag.pos_tag(tokens)
        for tag in tags:
            if tag[1] in useful_field:
                ret.append(tag[0])
                #ret.append(tag[0])
    return ret


lock1 = threading.Lock()
lock2 = threading.Lock()


def process_util(data, useful_field, ret):
    print len(data)
    lock2.acquire()
    cleaner = TagClean.TagClean()
    #send_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    lock2.release()
    count = 0
    for line in data:
        count += 1
        print count
        ret.extend(cleaner.process_single(line)[0])


def generate_all_emotion(file_name, useful_field, name):
    lock1.acquire()
    data = codecs.open(file_name, encoding='utf-8').readlines()
    lock1.release()
    ret_list = list()
    ret_1 = list()
    ret_2 = list()
    ret_3 = list()
    ret_4 = list()
    print len(data)
    thread_pool = list()
    thread_pool.append(threading.Thread(target=process_util, args=(data[0: 30000], useful_field, ret_1)))
    thread_pool.append(threading.Thread(target=process_util, args=(data[30000: 60000], useful_field, ret_2)))
    thread_pool.append(threading.Thread(target=process_util, args=(data[60000: 90000], useful_field, ret_3)))
    thread_pool.append(threading.Thread(target=process_util, args=(data[90000:], useful_field, ret_4)))
    # thread_pool.append(threading.Thread(target=process_util, args=(data[0: 3], useful_field, ret_1)))
    # thread_pool.append(threading.Thread(target=process_util, args=(data[3: 6], useful_field, ret_2)))
    # thread_pool.append(threading.Thread(target=process_util, args=(data[6: 9], useful_field, ret_3)))
    # thread_pool.append(threading.Thread(target=process_util, args=(data[9:], useful_field, ret_4)))
    for t in thread_pool:
        t.start()
    for t in thread_pool:
        t.join()
    ret_list = ret_1 + ret_2 + ret_3 + ret_4
    print type(ret_list)
    ret_counter = collections.Counter(ret_list)
    ret_counter = ret_counter.most_common(len(ret_counter))
    w = open('../dictionary/' + name + '_frequency.txt', 'wb')
    for item in ret_counter:
        w.write(item[0].encode('utf-8') + '\t' + str(item[1]) + '\n')
    w.close()


if __name__ == "__main__":
    #t1 = threading.Thread(target=generate_all_emotion, args=(Review_File, {'VBD', 'VBN', 'VB', 'VBP', 'VBZ'}, 'VB'))
    #t2 = threading.Thread(target=generate_all_emotion, args=(Review_File, {'JJ', 'JJR', 'JJS'}, 'JJ'))
    #t1.start()
    #t2.start()
    #t1.join()
    #t2.join()
    #generate_all_emotion(Review_File, {'VBD', 'VBN', 'VB', 'VBP', 'VBZ'}, 'VB')
    generate_all_emotion(Review_File, {'JJ', 'JJR', 'JJS'}, 'JJ_new_refined')
