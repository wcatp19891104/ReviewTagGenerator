import sys

from Prepare.DataClean.temp import GeneralUsage_pb2

#sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/hadoopy-0.6.0-py2.7-macosx-10.6-intel.egg')
sys.path.insert(0,'/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/')
from hadoop.io import SequenceFile
import os
print os.getcwd()


def extract_and_write(filename, out_file):
    ret = list()
    data = list()
    print os.getcwd()
    print open(filename).read()
    path = '/Users/wangzaicheng/Documents/workspace/ReviewTagGeneration/DataClean/temp/app01.osg-qa.fuhu.org-GeneralUsage.log-20150410_104000'
    reader = SequenceFile.Reader(path)
    key_class = reader.getKeyClass()
    value_class = reader.getValueClass()

    key = key_class()
    value = value_class()

    position = reader.getPosition()
    while reader.next(key, value):
        print '*' if reader.syncSeen() else ' ',
        print '[%6s] %6s %6s' % (position, key.toString(), value.toString())
        position = reader.getPosition()

    reader.close()
    # for line in data:
    #     curr_obj = GeneralUsage_pb2.GeneralUsagePro()
    #     #curr_obj.MergeFromString(line)
    #     text_format.Merge(line[0: -1], curr_obj)
    #     ret.append(curr_obj)
    # with open(out_file, "wb") as w:
    #     w.write('\n'.join([str(l) for l in ret]))


from hadoop.io import Text
from hadoop.io import SequenceFile


def writeData(writer):
    key = Text()
    value = Text()

    key.set('Key')
    value.set('Value')
    #key2 = Text()
    #value2 = Text()
    #key2.set("hehe")
    #value2.set("hehe")
    writer.append(key, value)
    #writer.append(key2, value2)



local_path = "local"


if __name__ == "__main__":




    reader = SequenceFile.Reader('app01.osg-qa.fuhu.org-GeneralUsage.log-20150410_104000.1')

    key_class = reader.getKeyClass()
    value_class = reader.getValueClass()

    key = key_class()
    value = value_class()

    position = reader.getPosition()
    array = reader._sync
    for a in array:
        unsigned = ord(a)
        signed = unsigned - 256 if unsigned > 127 else unsigned
        print signed
    ret = list()
    #array = [a & 1 for a in array]
    while reader.next(key, value):
        #print '*' if reader.syncSeen() else ' ',
        #print '[%6s] %6s %6s' % (position, key.toString(), value.toString())
        curr = GeneralUsage_pb2.GeneralUsagePro()
        curr.ParseFromString(value.toString())
        ret.append(curr)
        position = reader.getPosition()

    reader.close()
    print len(ret)
    #extract_and_write('app01.osg-qa.fuhu.org-GeneralUsage.log-20150410_104000', "out.txt")

