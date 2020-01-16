from flask import Flask
from flask import render_template, request, url_for, redirect
import csv
import matplotlib.pyplot as plt
from matplotlib import style
import os
import datetime
import collections
import json
import re
style.use('ggplot')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Create new data file

with open('data.csv', 'w', encoding='utf-8') as t:
    row = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
          % ('Имя', 'Пол', 'Год рождения', 'Родной язык',
             'Язык домашнего общения', 'Язык обучения в школе',
             'Язык матери', 'Язык отца')
    t.write(row)

# Get data from the data-file when needed


def getData(file):

    with open(file, encoding='utf-8') as f:
        f = csv.reader(f, delimiter='\t', quotechar='|')
        f = list(f)
        dict = {}
        for row in f:
            if row[0] == '':
                row[0] = 'Anonymous' + str(datetime.datetime.today())
            if row[0] not in dict:
                dict[row[0]] = row[1:]
            else:
                row[0] = row[0] + str(f.index(row))
                dict[row[0]] = row[1:]
    return dict

# Function for plotting a graph with home langs


def chartLangs(dict):

    home_langs = []
    home_langs_count = []
    for key, value in dict.items():
        if key == 3:
            for k, v in value.items():
                home_langs.append(k)
                home_langs_count.append(v)
    plt.bar(home_langs, home_langs_count)
    plt.ylabel('Количество в анкете')
    plt.xlabel('Язык')
    plt.xticks(home_langs)
    plt.yticks(home_langs_count)
    path = os.path.join('.', 'static')
    if not os.path.exists(path):
        os.makedirs(path)
    name = path + os.sep + 'home_lang_bars.jpg'
    if os.path.exists(name):
        os.remove(name)
    plt.savefig(name)

# Function for plotting a graph with mum langs


def chartMum(dict):

    mum_langs = []
    mum_langs_count = []
    for key, value in dict.items():
        if key == 5:
            for k, v in value.items():
                mum_langs.append(k)
                mum_langs_count.append(v)
    plt.bar(mum_langs, mum_langs_count)
    plt.xticks(mum_langs)
    plt.yticks(mum_langs_count)
    path = os.path.join('.', 'static')
    if not os.path.exists(path):
        os.makedirs(path)
    name = path + os.sep + 'mum_lang_bars.jpg'
    if os.path.exists(name):
        os.remove(name)
    plt.savefig(name)

# Function for plotting a graph with dad langs


def chartDad(dict):

    dad_langs = []
    dad_langs_count = []
    for key, value in dict.items():
        if key == 6:
            for k, v in value.items():
                dad_langs.append(k)
                dad_langs_count.append(v)
    plt.bar(dad_langs, dad_langs_count)
    plt.xticks(dad_langs)
    plt.yticks(dad_langs_count)
    path = os.path.join('.', 'static')
    if not os.path.exists(path):
        os.makedirs(path)
    name = path + os.sep + 'dad_lang_bars.jpg'
    if os.path.exists(name):
        os.remove(name)
    plt.savefig(name)

# Main function for filling in the form


@app.route('/')
def index():

    # Get the questions from file and accept answers

    with open('questions.txt', 'r', encoding='utf-8') as f:
        f = f.readlines()
    quest = {}
    for el in f:
        quest[el.split('\t')[0]] = el.split('\t')[1].strip()

    return render_template('index.html', quest=quest)

# Redirect user for feedback page and save his answers


@app.route('/feedback')
def answers():

    # Collect the data

    if request.args:
        name = request.args["name"]
        sex = request.args["sex"]
        year = request.args["year"]
        native_lang = request.args["native_lang"]
        home_lang = request.args["home_lang"]
        school_lang = request.args["school_lang"]
        mother_tongue = request.args["mother_tongue"]
        father_tongue = request.args["father_tongue"]

    # Write the data to the file

        with open('data.csv', 'a', encoding='utf-8') as t:
            if name == '':
                name = 'Anonymous' + str(datetime.datetime.today())
            row = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % \
                  (name, sex, year, native_lang,
                   home_lang, school_lang, mother_tongue,
                   father_tongue)

            t.write(row)

    return render_template('feedback.html')

# Make up a json-data page


@app.route('/json')
def jsonPage():
    dict = getData('data.csv')
    json_string = json.dumps(dict, ensure_ascii=False, indent=4)
    return json_string

# Count statistics


@app.route('/stats')
def stats():
    bigdata = {}

    # Create variables for statistics:

    m_lang = 0
    f_lang = 0
    both = 0
    franca = 0
    native_m = 0
    native_f = 0
    native_h = 0
    native_other = 0
    sc_h = 0
    sc_n = 0
    sc_o = 0

    for el in range(7):
        bigdata[el] = []
    dict = getData('data.csv')

    # Create a new dictionary to show the data on the page

    for key, value in dict.items():
        if key != 'Имя':
            for i in range(7):
                bigdata[i].append(value[i])

    # Count influence mother//father langs on choosing home lang

            if value[5] != value[6]:
                if value[5] == value[3]:
                    m_lang += 1
                elif value[6] == value[3]:
                    f_lang += 1
                else:
                    franca += 1
            else:
                if value[3] == value[5] and value[3]:
                    both += 1
                else:
                    franca += 1

    # Count influence of real lang on so-called 'native language'

            if value[2] == value[3]:
                native_h += 1
            elif value[2] == value[5]:
                native_m += 1
            elif value[2] == value[6]:
                native_f += 1
            else:
                native_other += 1

    # Count influence of home/native langs on school language

            if value[4] == value[3]:
                sc_h += 1
            else:
                if value[4] == value[2] and value[2] != value[3]:
                    sc_n += 1
                if value[4] != value[3] and value[4] != value[2]:
                    sc_o += 1

    # Count influence of home/native langs on school language
    if (sc_h + sc_n + sc_o) != 0:
        sc_h_prop = round(sc_h / (sc_h + sc_n + sc_o), 2) * 100
        sc_n_prop = round(sc_n / (sc_h + sc_n + sc_o), 2) * 100
        sc_o_prop = round(sc_o / (sc_h + sc_n + sc_o), 2) * 100
    else:
        sc_h_prop, sc_n_prop, sc_o_prop = 0, 0, 0

    # Count influence mother//father langs on choosing home lang

    if (m_lang + f_lang + franca + both) != 0:

        m_lang_prop = round(m_lang/(m_lang + f_lang +
                                    franca + both), 2) * 100
        f_lang_prop = round(f_lang / (m_lang + f_lang +
                                      franca + both), 2) * 100
        new_lang_prop = round(franca / (m_lang + f_lang +
                                        franca + both), 2) * 100
        both_lang_prop = round(both / (m_lang + f_lang +
                                       franca + both), 2) * 100
    else:
        m_lang_prop, f_lang_prop, new_lang_prop, both_lang_prop = 0, 0, 0, 0

    # Count influence of real lang on so-called 'native language'

    if (native_h + native_m + native_f + native_other) != 0:
        native_h_prop = round(native_h / (native_h + native_m +
                                          native_f + native_other), 2) * 100
        native_m_prop = round(native_m / (native_h + native_m +
                                          native_f + native_other), 2) * 100
        native_f_prop = round(native_f / (native_h + native_m +
                                          native_f + native_other), 2) * 100
        native_other_prop = round(native_other / (native_h +
                                                  native_m + native_f +
                                                  native_other), 2) * 100
    else:
        native_h_prop, native_m_prop, \
            native_f_prop, native_other_prop = 0, 0, 0, 0

    # Count total scores of each variant of answer

    for key, value in bigdata.items():
        bigdata[key] = collections.Counter(value)

    # Collect data for a chart:

    chartLangs(bigdata)
    chartMum(bigdata)
    chartDad(bigdata)

    return render_template('stats.html', data=dict, results=bigdata,
                           m_lang_prop=m_lang_prop, f_lang_prop=f_lang_prop,
                           new_lang_prop=new_lang_prop,
                           both_lang_prop=both_lang_prop,
                           native_h_prop=native_h_prop,
                           native_m_prop=native_m_prop,
                           native_f_prop=native_f_prop,
                           native_other_prop=native_other_prop,
                           sc_h_prop=sc_h_prop,
                           sc_n_prop=sc_n_prop,
                           sc_o_prop=sc_o_prop)

# Create page for search


@app.route('/search')
def search():
    return render_template('search.html')

# Page for found results


@app.route('/results')
def results():
    found = {}
    lang = ''
    nat = False

    # Check request:

    if request.args:
        lang = request.args["language"]
        nat = True if 'native' in request.args else False
    dict = getData('data.csv')    # Search in the data table
    for key, value in dict.items():
        if lang in value:
            if nat is False:
                found[key] = value
            else:
                if lang == value[2]:
                    found[key] = value
    return render_template('results.html', found=found, language=lang,
                           nat=nat)


if __name__ == '__main__':
    app.run(debug=True)
