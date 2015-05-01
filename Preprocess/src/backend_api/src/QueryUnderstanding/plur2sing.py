# -*- coding: utf-8 -*-
__author__ = 'wangzaicheng'
import inflect
import re
import os

ABS_PATH = os.path.dirname(os.path.realpath(__file__))
#plur_2_singular_exception_file = '/'.join(ABS_PATH.split('/')[: -1]) + '/resource/exceptions/plur_exception.txt'
plur_2_singular_exception_file = ABS_PATH + '/../../resource/exceptions/plur_exception.txt'
Special_Char_File = ABS_PATH + '/../../resource/exceptions/special_char.txt'
#all_words_file = '/'.join(ABS_PATH.split('/')[: -1]) + '/resource/table/allwords.txt'
all_words_file = ABS_PATH + '/../../resource/table/allwords.txt'
#plur_2_singular_exception_file = '../resource/exceptions/plur_exception.txt'
double_ss = re.compile('ss$')
single_ies = re.compile('ies$')
pure_alpha = re.compile('[a-zA-Z-\ ]+$')
useless_char = {'-',  '|', '"', "'", '!', '&', '/', '\\', ':', ",", ";"}
seperate_char = {',', ';', '-'}
useless_except = 'w/'


class Plur2Sing:
    def __init__(self):
        """initial plural to singular class

        load essential file:
        plur_2_singular_exception_file: the exception list for plural to singular transform
        """
        self.engine = inflect.engine()
        self.first_level = dict()
        self.allword = {line.strip().lower() for line in open(all_words_file).readlines()}
        self.special_normalizer = {line.strip().split('\t')[0]: line.strip().split('\t')[2] for line in open(Special_Char_File).readlines()}
        f = open(plur_2_singular_exception_file, "r")
        while True:
            line = f.readline().strip()
            if not line:
                break
            temp = line.split("\t")
            self.first_level[temp[0]] = temp[1]
        f.close()

    def tosingular(self, plural):
        """perform plural to singular transform

        :param plural: a word in plural or singular form
        :return: string: the singular form of the input word
        """
        if type(plural) == str:
            plural = plural
        plural = plural.lower()
        for key in self.special_normalizer:
            plural = plural.replace(key, self.special_normalizer[key])
        if '-' == plural:
            return plural
        if ('-' in plural or '"' in plural) and plural in self.allword and '-' != plural[-1]:
            return plural.lower()
        plural = plural.lower()
        #for char in seperate_char:
        #    plural = plural.replace(char, ' ' + char + ' ')
        for char in useless_char:
            if useless_except not in plural:
                if char in seperate_char:
                    plural = plural.replace(char, ' ' + char + ' ')
                else:
                    plural = plural.replace(char, ' ')
        if len(plural) <= 3:
            return plural
        #if string[0] >= u"\u4E00" and string[0] <= u"\u9FA5":
         #   return string
        if plural in self.first_level.keys():
            return self.first_level[plural]
        if double_ss.search(plural) is not None and single_ies.search(plural) is None or pure_alpha.match(plural) is \
                None:
            return plural
        try:
            return self.engine.singular_noun(plural) if self.engine.singular_noun(plural) is not False else plural
        except StandardError:
            return plural

    def normalize_line(self, line):
        #if '-' in line and line in self.allword:
        #    return line.lower()
        if line[0] == '#':
            return line
        line = line.strip().lower()
        if line[:4] == "the ":
            line = line[4:]
        return ' '.join([self.tosingular(w.strip().lower()) for w in line.split(' ')]).replace('   ', ' ').replace('  ', ' ').strip()

if __name__ == "__main__":
    p2s = Plur2Sing()
    #p2s.engine.
    #print p2s.tosingular("police")
    print p2s.normalize_line("Similac For Supplementation Infant Formula Powder, 1.45lb container")
    pass
    #print Plur2Sing.__doc__