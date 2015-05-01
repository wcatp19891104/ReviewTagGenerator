__author__ = 'wangzaicheng'

"Use writetb to put data on HDFS with demo that writes local directory contents to HDFS"
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/hadoopy-0.6.0-py2.7-macosx-10.6-intel.egg')
import hadoopy
import os

hdfs_path = 'data_in_ex0.seq.tb'


def read_local_dir(local_path):
    for fn in os.listdir(local_path):
        path = os.path.join(local_path, fn)
        if os.path.isfile(path):
            yield path, open(path).read()


def main():
    local_path = './file/'
    hadoopy.writetb(hdfs_path, read_local_dir(local_path))

if __name__ == '__main__':
    main()