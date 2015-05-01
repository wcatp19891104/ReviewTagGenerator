# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'


import sys


def add_to_remove_list(file_name):
    remove_set = set()
    with open(file_name) as r:
        for line in r.readlines():
            remove_set.add(line.strip())
    data = open("frequency_change.txt", "r").read()
    to_string = str()
    for item in remove_set:
        to_string += "remove" + "\t" + item + "\n"
    with open("frequency_change.txt", "wb") as w:
        w.write(data + "\n" + to_string)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        add_to_remove_list("remove.txt")
    else:
        add_to_remove_list(sys.argv[1])