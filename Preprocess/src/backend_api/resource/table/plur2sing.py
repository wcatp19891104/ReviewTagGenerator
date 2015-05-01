__author__ = 'wangzaicheng'
import inflect
import re

plur_2_singular_exception_file = '../exceptions/plur_exception.txt'
#plur_2_singular_exception_file = '../resource/exceptions/plur_exception.txt'
double_ss = re.compile('ss$')
single_ies = re.compile('ies$')
pure_alpha = re.compile('[a-zA-Z-\ ]+$')
useless_char = {',', '|', '"', "'", '!', '&', '(', ')', '/', '\\'}
useless_except = 'w/'


class Plur2Sing:
    def __init__(self):
        """initial plural to singular class

        load essential file:
        plur_2_singular_exception_file: the exception list for plural to singular transform
        """
        self.engine = inflect.engine()
        self.first_level = dict()

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
        for char in useless_char:
            if useless_except not in plural:
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
        if line[0] == '#':
            return line
        line = line.strip().lower()
        if line[:4] == "the ":
            line = line[4:]
        return ' '.join([self.tosingular(w.strip().lower()) for w in line.split(' ')]).replace('   ', ' ').replace('  ', ' ')

if __name__ == "__main__":
    p2s = Plur2Sing()
    #p2s.engine.
    print p2s.tosingular("police")
    print p2s.normalize_line("caps")
    #print Plur2Sing.__doc__