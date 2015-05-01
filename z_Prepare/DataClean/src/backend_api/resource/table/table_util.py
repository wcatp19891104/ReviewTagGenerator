__author__ = 'wangzaicheng'

file_set = {"character.txt", "demography.txt", "products.txt"}
special_char = {'-', ',', '|', '"', "'", '!', '&', '(', ')', '/', '\\'}
brand_file_set = {"brands.txt", "brand_model_mapping.txt"}
all_words = "allwords.txt"
frequency_file = "key_frequency.txt"
products_file = "products.txt"
new_products = "new_products.txt"


def has_special(string):
    for char in special_char:
        if char in string:
            return True
    return False


def generate_all_words():
    name_set = set()
    for file in file_set:
        lines = open(file).readlines()
        for line in lines:
            line = line.strip()
            if has_special(line):
                name_set.add(line)
    for file in brand_file_set:
        lines = open(file).readlines()
        for line in lines:
            line = line.strip().split('\t')
            for string in line:
                if has_special(string):
                    name_set.add(string)
                for part in string.split(' '):
                    if has_special(part):
                        name_set.add(part)
    w = open(all_words, 'wb')
    for item in name_set:
        w.write(item + '\n')
    w.close()


def generate_new_products():
    all_products = set()
    remove_product = list()
    products = set()
    with open(products_file, 'rd') as f:
        for line in f.readlines():
            all_products.add(line.lower().strip())

    with open(frequency_file, 'rd') as f:
        for line in f.readlines():
            line = line.strip().split('\t')
            if len(line) > 3 and len(line[1].split(' ')) > 1:
                remove_product.append(line[1])
    remove_product = remove_product[-500:]
    for item in all_products:
        if item not in remove_product:
            products.add(item)
    w = open(new_products, 'wb')
    for item in products:
        w.write(item + '\n')
    w.close()

if __name__ == "__main__":
    #generate_new_products()
    generate_all_words()
