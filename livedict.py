# -*- coding: utf-8 -*-
"""
Quiz flask blueprint
"""

import re
import yaml
import os
import time
import hashlib
import json
import pickle

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

from lib import construct_dataset as cs
from lib.corpus import Corpus

from pathlib import Path
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, Response, session
)
from app.mod.quiz_factory import Quiz
from app.auth import login_required
from random import randint

from app.mod.livedict import functions
from scipy.spatial.distance import cosine
from sklearn.linear_model import LogisticRegression

global blueprints_types
BP = Blueprint('livedict', __name__, subdomain='livedict') if os.environ.get('BLUEPRINTS_TYPES', "domains") == "domains" else Blueprint('livedict', __name__, url_prefix='/livedict')

class BinSearchDict:
    def __init__(self, init_dict):
        keys = list(init_dict.keys())
        keys.sort()
        self.data = [(x, init_dict[x]) for x in keys]

    def __getitem__(self, name):
        a, b = 0, len(self.data)
        while b - a > 1:
            c = (b + a) // 2
            if self.data[c][0] == name:
                return self.data[c][1]

            if self.data[c][0] > name:
                b = c
            else:
                a = c
        raise Exception("can't find word")


def init_app(app):
    ''' During app initialization'''
    with open(os.path.join(app.instance_path,"livedict","structure.json"), "r") as f:
        BP.structure = json.load(f)
        BP.structure[1]['19'] = 'Отрицательное — Положительное' # 'Одобрительность'
        BP.structure[1]['20'] = 'Неважное — Важное' # 'Важность'
        BP.structure[1]['21'] = 'Аггресивное — Примирительное' # 'Агрессивность'
        BP.structure[1]['22'] = 'Отстранённое — Интимное' # 'Близость'

        BP.structure[0][BP.structure[1]['19']] = [[0,''], [1, '']] # [[0,'Отрицательное'], [1, 'Положительное']]
        BP.structure[0][BP.structure[1]['20']] = [[0,''], [1, '']] # [[0,'Неважное'], [1, 'Важное']]
        BP.structure[0][BP.structure[1]['21']] = [[0,''], [1, '']] # [[0,'Аггресивное'], [1, 'Примирительное']]
        BP.structure[0][BP.structure[1]['22']] = [[0,''], [1, '']] # [[0,'Отстранённое'], [1, 'Интимное']]


    with open(os.path.join(app.instance_path,"livedict", "pkl", "corpus.pkl"), "rb") as f:
        BP.corpus_full = pickle.load(f)
        # del BP.corpus_full.texts
        # del BP.corpus_full.data
        # del BP.corpus_full.ind

    with open(os.path.join(app.instance_path,"livedict", "pkl_old", "structure.pkl"), "rb") as f:
        BP.structure_OLD = pickle.load(f)
    with open(os.path.join(app.instance_path,"livedict", "pkl_old", "word_dict_inv.pkl"), "rb") as f:
        tmp = pickle.load(f)
    BP.inv_dict_OLD = BinSearchDict(tmp)

    BP.structure_OLD[1][''] = [(0, "отрицательное — положительное")]
    BP.structure_OLD[1]['Социально-сословная специфика'][0] = (0, "отсутствует")
    BP.structure_OLD[1]['Форма речи 1'] = [(0, "стих — проза")]
    BP.structure_OLD[1]['Форма речи 2'] = [(0, "монолог — диалог")]
    BP.structure_OLD[1]['Форма речи 3'] = [(0, "паремия — развернутый текст")]
    BP.structure_OLD[1]['Профессиональная специфика'] = [(0, "отсутствует — присутствует")]
    BP.structure_OLD[1]['Дата'][0] = (0, "неизвестная")

    np.seterr('raise')

@BP.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    g.url_prefix = 'livedict'



# (data.field3, 3),
# (data.field7, 7),
# (data.field8, 8),
# (data.field9, 9),
# - (data.field11, 11),
# (data.field12, 12),
# (data.field13, 13),
# (data.field14, 14),
# (data.field15, 15),
# (data.field16, 16),
# (data.field17, 17),
# - (data.field19, 19),
# - (data.field20, 20),
# - (data.field21, 21),
# - (data.field22, 22),


@BP.route("/", methods=["GET", "POST"])
def index():
    """
    Draw list of quizes
    """
    return render_template("livedict/index.html", list=current_app.quizes_list)


@BP.route("/text", methods=["GET", "POST"])
def predict_text():

    res = []

    if request.method == "POST":
        text = request.form["word"]
        text = text.lower()
        text = re.sub(r"-", "", text)
        text = re.sub(r"[\d\W_\sA-Za-z]+", " ", text)

        with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"model_7.pkl"), "rb") as f:
            model = pickle.load(f)
        with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"quantiles_7.pkl"), "rb") as f:
            quantiles = pickle.load(f)

        lines = [i[1] for i in BP.structure[0][BP.structure[1]['7']]]

        words = text.split()

        # colors = []
        dst = functions.predict_word(text, BP.corpus_full, model, length=10, activation="linear", norm=True)
        # for word in words:
        #     trg = functions.predict_word(word, BP.corpus_full, model, length=len(words), activation="linear", norm=True)
        #     c = cosine(dst, trg)
        #     colors.append((word, 1 if np.isnan(c) else c, trg))

        _img = BytesIO()
        plt.figure()
        plt.barh(lines, 2 * dst - 1)
        plt.xlim((-1,1))
        plt.title('стилистика текста')
        plt.savefig(_img, format="svg", bbox_inches='tight', transparent=True)
        res.append(re.sub(r'<style[^<]*</style>','',re.sub(r'(font-[^;]*;|\n\s*)', r'',_img.getvalue().decode("utf8"))))

        # res.append(functions.color_text(colors))

        return render_template("livedict/text.html", images=res, word=text)
    return render_template("livedict/text.html")




@BP.route("/word_alpha", methods=["GET", "POST"])
def predict_word():

    res = []

    if request.method == "POST":
        text = request.form["word"]
        text = re.sub(r"-", "", text)
        text = re.sub(r"[\d\W_\sA-Za-z]+", " ", text)
        print(text)
        skip = {'3':1, '7':0, '8':1, '9':1, '12':1, '13':0, '14':1, '15':0, '16':0, '17':0, '19':1, '20':1, '21':1, '22':1}
        for n in ('7'):
            print(n)
            with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"model_{n}.pkl"), "rb") as f:
                model = pickle.load(f)
            with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"quantiles_{n}.pkl"), "rb") as f:
                quantiles = pickle.load(f)

            lines = [i[1] for i in BP.structure[0][BP.structure[1][n]]]

            if n == '19':
                res.append(functions.plot_word_stats(model, BP.corpus_full, text, activation="sigmoid", scale=10, length=10, lines=lines, title=BP.structure[1][n], skip=skip[n]))
            else:
                res.append(functions.plot_word_stats(model, BP.corpus_full, text, quantiles, scale=10, length=10, lines=lines, title=BP.structure[1][n], skip=skip[n]))
            model = None
            quantiles = None

        return render_template("livedict/word.html", images=res, word=text)
    return render_template("livedict/word.html")


@BP.route("/json", methods=["GET", "POST"])
def predict_word_json_OLD():

    if request.method == "POST":
        word = request.form["word"]
        # images = functions.get_word_imgs(word, BP.structure_OLD, BP.inv_dict_OLD, os.path.join(current_app.instance_path, "livedict", "pkl_old"))
        try:
            datas = functions.get_word_dict(word, BP.structure_OLD, BP.inv_dict_OLD, os.path.join(current_app.instance_path, "livedict", "pkl_old"))
            return Response(json.dumps(datas), mimetype='text/json')
        except ValueError:
            print(f"В базе данных нет слова {word}!")

        return Response('', mimetype='text/json')

    return Response('', mimetype='text/json')

@BP.route("/json_alpha", methods=["GET", "POST"])
def predict_word_json():

    if request.method == "POST":
        text = request.form["word"]
        text = re.sub(r"-", "", text)
        text = re.sub(r"[\d\W_\sA-Za-z]+", " ", text)
        json_data = {}

        skip = {'3':1, '7':0, '8':1, '9':1, '12':1, '13':0, '14':1, '15':0, '16':0, '17':0, '19':1, '20':1, '21':1, '22':1}
        for n in ('7', '3', '9', '12', '14', '15', '16', '17','19'):
            print(n)
            with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"model_{n}.pkl"), "rb") as f:
                model = pickle.load(f)
            with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"quantiles_{n}.pkl"), "rb") as f:
                quantiles = pickle.load(f)

            lines = [i[1] for i in BP.structure[0][BP.structure[1][n]]]

            if n == '19':
                json_data[BP.structure[1][n]] = functions.get_word_stats(model, BP.corpus_full, text, activation="sigmoid", scale=10, length=10, lines=lines, title=BP.structure[1][n], skip=skip[n])
            else:
                json_data[BP.structure[1][n]] = functions.get_word_stats(model, BP.corpus_full, text, quantiles, scale=10, length=10, lines=lines, title=BP.structure[1][n], skip=skip[n])
            model = None
            quantiles = None

        return Response(json.dumps(json_data), mimetype='text/json')
    return Response('', mimetype='text/json')


@BP.route("/word", methods=["GET", "POST"])
def predict_word_OLD():

    if request.method == "POST":
        word = request.form["word"]
        images = None

        # images = functions.get_word_imgs(word, BP.structure_OLD, BP.inv_dict_OLD, os.path.join(current_app.instance_path, "livedict", "pkl_old"))
        try:
            images = functions.get_word_imgs(word, BP.structure_OLD, BP.inv_dict_OLD, os.path.join(current_app.instance_path, "livedict", "pkl_old"))
            datas = [3, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17]
        except ValueError as e:
            print(f"В базе данных нет слова {word}!")

        return render_template("livedict/word_old.html", images=images, word=word)

    return render_template("livedict/word_old.html")


@BP.route("/hist", methods=["GET", "POST"])
def history_word():

    res = []

    if request.method == "POST":
        text = request.form["word"]
        idx_x = dict(BP.structure[0]["Дата"])
        idx_y = dict(BP.structure[0]["Стиль"])

        with open(os.path.join(current_app.instance_path, "livedict", "pkl", f"model_hist.pkl"), "rb") as f:
            models = pickle.load(f)
        res.append(functions.predict_word_hist(text, models, idx_x, idx_y, 5, 10))

        return render_template("livedict/word.html", images=res, word=text)
    return render_template("livedict/word.html")


@BP.route('/application')
def applic():
    title = "Приложение"
    return render_template("livedict/application.html")
