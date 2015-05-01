__author__ = 'wangzaicheng'

#import bytearrayt
import base64

#data = open("test.seq", "rb").read()
#print data
#print base64.b32decode("data")

import sys



import os

if __name__ == '__main__':
    data = open('a.seq', 'rb')
    ba = bytearray(data.read())
    for byte in ba:
        print byte & 1
    print ""
    b = [0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0]
