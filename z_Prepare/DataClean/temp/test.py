__author__ = 'wangzaicheng'
import json

buffer = open("app01.osg-qa.fuhu.org-WishlistUsage.log-20150423_005514.1.log").read()
#buffer 就是那个要解的string
temp = buffer.strip().split(':')
string = ':'.join(temp[1:]).replace('\n', '')
data = json.loads(string)
print ""
