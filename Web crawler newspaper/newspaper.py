import sqlite3
import csv
import re
from flask import Flask, render_template, request, url_for, redirect
from pymystem3 import Mystem
import json
from flask_paginate import Pagination, get_page_args


# Функция читает таблицу с мета-данными, обходит папку с корпусом и создает БД

def data_base():
    conn = sqlite3.connect('paper_corpus.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS paper_base"
              "(id, head, plain, lemma, source, created)")
    id_table = 0
    with open('metadata.csv', 'r', encoding='utf-8') as f:
        f = f.readlines()
    for row in f[1:]:
        row = row.split('\t')

        # Тексты кладутся в БД, из plain удаляются начальные теги @

        with open(row[0], 'r', encoding='utf-8') as t:
            plain = t.read()
            plain = re.sub('@.+?\n', '', plain)
        path_mystem = row[0].replace('plain', 'mystem-plain')
        with open(path_mystem, 'r', encoding='utf-8') as t:
            lemma = t.read()

        c.execute("INSERT INTO paper_base VALUES (?, ?, ?, ?, ?, ?)",
                  (id_table, row[2], plain, lemma, row[10], row[3]))
        id_table += 1
    conn.commit()
    conn.close()


app = Flask(__name__)


# Основная функция, в которой создается страница и выводятся результаты поиска

@app.route('/')
def index():

    query = ''
    found = []
    symbs = "1234567890,—[]№!\"\'«»».»,?.,;:|/*{}<>@#$%-^& )("
    conn = sqlite3.connect('paper_corpus.db')
    c = conn.cursor()

    if request.args:
        text = request.args["word"]
        query = text
        m = Mystem()
        lemmas = m.lemmatize(text)
        only_words = list(lemmas[0:-1:2])
        word = only_words[0]
        word = "%{" + word + '=%'

        # Поиск всех форм слова

        if len(only_words) == 1:

            for row in c.execute("SELECT head, plain, lemma, source FROM "
                                 "paper_base WHERE lemma LIKE ?", (word,)):
                lemma = row[2].split('}')
                word = word.strip('%')
                sep_plain = row[1].split()

                # В каждой найденной ячейке БД поиск слова

                for n, w in enumerate(lemma):
                    if re.search(word, w, re.IGNORECASE):
                        if n < 100 and (n + 100) > len(sep_plain):
                            plain = ' '.join(sep_plain)
                        elif n < 100:
                            plain = ' '.join(sep_plain[:(n + 100)])
                        elif (n + 100) > len(sep_plain):
                            plain = ' '.join(sep_plain[(n - 100):])
                        else:
                            plain = ' '.join(sep_plain[(n - 100):(n + 100)])
                        found.append((row[0], plain, row[3]))

        # Поиск всех форм фразы

        else:
            for row in c.execute("SELECT head, plain, lemma, source FROM "
                                 "paper_base WHERE lemma LIKE ?", (word,)):

                # Очистка текста с разметкой от тегов

                lemma = row[2]
                lemma = re.sub('=.+?}', '', lemma)
                lemma = re.sub('{', '', lemma)

                # Поиск в чистом тексте чистой фразы в начальной форме:

                if re.search(' '.join(only_words), lemma, re.IGNORECASE):
                    n = [i.strip(symbs) for i in lemma.split()]\
                        .index(only_words[-1])
                    sep_plain = row[1].split()
                    if n < 100 and (n + 100) > len(sep_plain):
                        plain = ' '.join(sep_plain)
                    elif n < 100:
                        plain = ' '.join(sep_plain[:(n + 100)])
                    elif (n + 100) > len(sep_plain):
                        plain = ' '.join(sep_plain[(n - 100):])
                    else:
                        plain = ' '.join(sep_plain[(n - 100):(n + 100)])
                    found.append((row[0], plain, row[3]))

    conn.close()
    return render_template('index.html', found=found, query=query)


def main():
    data_base()
    index()


if __name__ == '__main__':
    app.run(debug=True)
