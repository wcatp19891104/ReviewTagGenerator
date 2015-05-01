__author__ = 'wangzaicheng'


import sys
import os

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, FILE_PATH + '/../')
sys.path.insert(0, FILE_PATH + '/../../')


print "path added"