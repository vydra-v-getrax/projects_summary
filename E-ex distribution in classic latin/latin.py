import re
from collections import Counter
import urllib.request
import urllib.parse
import matplotlib.pyplot as plt
import numpy as np

VOWELS = 'aeiouy'

def compare(ex, e):
    all_letters = {}
    data = {}
    for key, value in ex.items():
        if key in e:
            all_letters[key] = (value, e[key])
        else:
            all_letters[key] = (value, 0)
    return all_letters

with open('results_cons.csv', 'a', encoding='utf-8') as t:
    for k, v in sorted(all_letters.items()):
        if k not in VOWELS:
            all_letters[k] = [v[0], v[1]]
            row = '%s\t%s %s\t%s %s\t%s\t%s\n' \
              %(k, str(round((int(v[0])/(int(v[0])+int(v[1])))*100)),
                '%', str(round((int(v[1])/(int(v[0])+int(v[1])))*100)),
                '%', str(v[0]), str(v[1]))
            t.write(row)

with open('results_vowels.csv', 'a', encoding='utf-8') as t:
    for k, v in sorted(all_letters.items()):
        if k in VOWELS:
            all_letters[k] = [v[0], v[1]]
            row = '%s\t%s %s\t%s %s\t%s\t%s\n' \
              %(k, str(round((int(v[0])/(int(v[0])+int(v[1])))*100)),
                '%', str(round((int(v[1])/(int(v[0])+int(v[1])))*100)),
                '%', str(v[0]), str(v[1]))
            t.write(row)

def letters(file):
    found_EX = []
    found_E = []
    with open(file, 'r', encoding='utf-8') as f:
        f = f.readlines()
    for paragraph in f:
        r = re.findall(' ex (.?)', paragraph, flags=re.IGNORECASE)
        if r:
            found_EX += r
        k = re.findall(' e (.?)', paragraph, flags=re.IGNORECASE)
        if k:
            found_E += k
    found_EX = list(map(lambda i:i.lower(), found_EX))
    found_E = list(map(lambda i: i.lower(), found_E))
    EX = Counter(found_EX)
    E = Counter(found_E)
    return compare(EX, E)

def graph():
    dictC = letters('CEASAR.txt')
    dictT = letters('LIVY.txt')
    freq = {}
    x = []
    e_C = []
    e_T = []
    for k, v in sorted(dictC.items()):
       if k not in VOWELS and k != ' ':
           x.append(k)
           e_C.append(round((v[1] / (int(v[0]) + int(v[1]))) * 100))

    for k, v in sorted(dictT.items()):
        if k not in VOWELS and k != ' ':
            e_T.append(round((v[1] / (int(v[0]) + int(v[1]))) * 100))
            freq[k] = e_T[-1]

    n_groups = 15
    means_frank = e_C
    means_guido = e_T

    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, means_frank, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Ceasar')

    rects2 = plt.bar(index + bar_width, means_guido, bar_width,
                     alpha=opacity,
                     color='g',
                     label='Tit Livi')

    plt.xlabel('Согласные')
    plt.ylabel('Процент вхождений')
    plt.title('Распределение Е')
    plt.xticks(index + bar_width, x)
    plt.legend()

    plt.tight_layout()
    #plt.show()

def plain_text(text):
    text = re.sub('<.+?>', '', text)
    text = re.sub('(\*)|(&.+? )', '', text)
    return text

def clean():
    with open('LIVY.txt', 'r', encoding='utf-8') as f:
        f = f.read()
        f = plain_text(f)
    with open('LIVY.txt', 'w', encoding='utf-8') as t:
        t.write(f)

# Get page source and read as a 'str' object
def downloadPage(page_url):
    try:
        page = urllib.request.urlopen(page_url)
        text = page.read().decode('utf-8')
        return text
    except:
        print("Error at: ", page_url)

# Function crowls pages and downloads text

def getText():
    common_url = 'http://www.thelatinlibrary.com/livy/liv.'
    all_text = []
    for i in range(27, 46):
        page_url = common_url + str(i) + '.shtml'
        print(page_url)
        
        # Check and correct ascii-symbols

        page_url = urllib.parse.urlsplit(page_url)
        page_url = list(page_url)
        page_url[2] = urllib.parse.quote(page_url[2])
        page_url = urllib.parse.urlunsplit(page_url)
        text = downloadPage(page_url)
        all_text.append(plain_text(text))
    with open('LIVY.txt', 'a', encoding='utf-8') as t:
        t.write('\n'.join(all_text))

def main():
    graph()

if __name__ == '__main__':
    main()