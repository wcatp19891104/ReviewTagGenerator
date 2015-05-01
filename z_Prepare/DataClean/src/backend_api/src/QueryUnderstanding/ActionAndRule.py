__author__ = 'wangzaicheng'

import re

from src.QueryUnderstanding import plur2sing


class Rule:
    def __init__(self, pattern=None, name=None):
        self.pattern = re.compile(pattern)
        self.name = name

    def run(self, word):
        if self.pattern.match(word) is not None:
            return [(word, [self.name])]
        return None

    #def __hash__(self):
    #    return 1000

    def __str__(self):
        return str(self.pattern)


class AgeRule(Rule):
    def __init__(self, pattern=None, name=None):
        Rule.__init__(self, pattern, name)

    def run(self, word):
        m = self.pattern.match(word)
        if m is not None:
            age = m.group(1)
            unit = m.group(3)
            if unit == 'month':
                return [(age, [self.name])]
            else:
                return [(str(int(age) * 12), ['age_low'])]


class RangeRule(Rule):
    def __init__(self, pattern=None, name=None):
        Rule.__init__(self, pattern, name)

    def run(self, word):
        if self.pattern.match(word) is None:
            return None
        m = self.pattern.match(word)
        start = m.group(1)
        end = m.group(7)
        unit = m.group(3)
        return [(start + ' - ' + end + ' ' + unit, [self.name])]


class RangeAge(Rule):
    def __init__(self, pattern=None, name=None):
        Rule.__init__(self, pattern, name)

    def run(self, word):
        if self.pattern.match(word) is None:
            return None
        m = self.pattern.match(word)
        start = m.group(1)
        end = m.group(7)
        unit = m.group(9)
        if unit in {'month', 'mon', 'm'}:
            return [(start, ['age_low']), (end, ['age_high'])]
        else:
            return [(str(int(start) * 12), ['age_low']), (str(int(end) * 12), ['age_high'])]


class Range(Rule):
    def __init__(self, pattern=None, name=None):
        Rule.__init__(self, pattern, name)

    def run(self, word):
        if self.pattern.match(word) is None:
            return None
        return [(word.replace('to', '-'), [self.name])]


class Normalizer(plur2sing.Plur2Sing):
    pass


class TagRule:
    def __init__(self, file_name, name):
        self._normalizer = Normalizer()
        self.list = self.read_file(file_name)
        self.name = name

    def read_file(self, file_name):
        ret = set()
        for line in open(file_name):
            ret.add(self._normalizer.normalize_line(line))
            #self._denormalize[self._normalizer.normalize_line(line)] = line.strip()
        return ret

    def run(self, word):
        if word in self.list:
            return self.name
        return None


class TagRuleBrand(TagRule):
    def __init__(self, file_name, name):
        TagRule.__init__(self, file_name, name)

    def read_file(self, file_name):
        pass


def match_quantity_and_unit(text):
    """
    Match quantity and its unit from product title (most likely)
    :param text:
    :return: (quantity, unit) as a tuple
    """

    # regex: [quantity_index, unit_index]
    patterns_map = {
        # hierarchical since multiple potential units could exist: "Breast Milk Storage Bottles 4oz 4pk"
        "([\d.]+)[\s-]*((sheet[s]?)|(pc)|(pk)|(count[s]?)|(pack[s]?)|(piece[s]?)|(pair[s]?)|(box?)|(boxes?))": [1, 2],
        # 12 lbs, 12-lbs
        "([\d.]+)[\s-]*((liter[s]?)|(lb[s]?)|(ounce[s]?)|(oz)|(fl. oz))": [1, 2],
        # pack of 3
        "(pack[s]?|box|set[s]?|)[\s]*of[\s]*([\d.]+)": [2, 1]
    }

    quantity = ""
    unit = ""
    for reg, idx in patterns_map.items():
        match = re.search(reg, text, re.IGNORECASE)
        if match:
            try:
                quantity = float(match.group(idx[0]).lower())
                unit = match.group(idx[1]).lower()
            except Exception:
                print "error parsing price: " + match.group(idx[0])
                return 0.0, ""
            break

    # normalize unit
    if unit.lower() in ['fl. oz', 'oz', 'ounce', 'ounces']:
        unit = 'oz'
    if unit.lower() in ['lb', 'lbs', 'pound', 'pounds']:
        unit = 'lb'
    if unit.lower() in ['liter', 'liters']:
        unit = 'liter'

    # normalize quantity
    if unit == 'lb':
        try:
            quantity = str(float(quantity) * 16)
            unit = 'oz'
        except Exception:
            pass

    if unit == 'liter':
        try:
            quantity = str(float(quantity) * 1000)
            unit = 'ml'
        except Exception:
            pass

    return quantity, unit


if __name__ == "__main__":
    print match_quantity_and_unit("15 pack diaper")
    #test for git
    '''
    t = TagRule('../resource/table/products.txt', 'product')
    print t.run('diaper')
    pass
    '''

