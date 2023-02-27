# -*- coding: utf-8 -*-

import os
import re
from app.mod.text_mikl import text_processing as MTP
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, ifft
from scipy.ndimage.filters import gaussian_filter1d
# from scipy.interpolate import make_interp_spline, BSpline
from scipy.stats.stats import pearsonr

from io import BytesIO

from flask import (
    Blueprint, g, render_template, request, Response, flash   # , current_app, redirect, session, url_for
)

BP = Blueprint('mikl', __name__, subdomain='phonotext') if os.environ.get('BLUEPRINTS_TYPES', "domains") == "domains" else Blueprint('mikl', __name__, url_prefix='/phonotext')


@BP.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    g.url_prefix = 'mikl'


def init_app(app):
    pass


@BP.route('/', methods=('GET', 'POST'))
@BP.route('/', methods=('GET', 'POST'))
def index():
    return render_template('mikl/index.html')


def calc_request(request):
    filter_min, filter_max = map(float, request.form['filter'].split(','))

    test_conf = MTP.CONFIG[request.args['lng']]

    test_conf[5] = MTP.CombinationsEvent(2, MTP.get_filter_com_rus(filter_min, filter_max))
    text = MTP.Phonotext(request.form['text'])
    for test in test_conf:
        MTP.PROCESSOR.handle(text, test)
    # repeats = list(text.repeats.values())
    # repeats.sort(key=lambda x: x.power[0], reverse=True)
    return text.repeats, text, filter_min, filter_max

def FH(x):
    '''ступенчатая функция Хэвисайда'''
    if x >= 0:
        q = 1
    else:
        q = 0
    return q

def get_pwr(a, b):
    '''сила взаимодействия двух повторов'''
    pwr = 0
    mul = 1
    dist = b.syll - a.syll
    dist_w = b.word - a.word
    if 1 < dist < 50:
        pwr = 1 / dist + 1 / max(1, dist_w)
        if a.origin == b.origin:
            mul += 1
        if a.w_pos[0] == b.w_pos[0]:
            mul += 1
        if a.w_pos[1] == b.w_pos[1]:
            mul += 1
        return pwr * mul
    return 0


@BP.route('/work', methods=('GET', 'POST'))
def edit():

    plt.rcParams["svg.fonttype"] = "none"

    if request.method != 'POST' or request.form['text'] == "":
        if request.args['lng'] == "rus":
            return render_template('mikl/base.html')
        return render_template('mikl/base_eng.html')


    repeats, test_text, filter_min, filter_max = calc_request(request)
    txt = []
    for letter in test_text.basetext:
        txt.append(f'<span class="l{letter.number} s{letter.syll} w{letter.word}">{letter.origin}</span>')

    txt = ''.join(txt).replace('\n', '<br/>')
    spmax = '<br/>'.join([f'{i+1}: {x.get_printable()}' for i, x in enumerate(test_text.SP)])
    comb = '<br/>'.join([
        '-'.join([
            ''.join([z.printable for z in y[0]]) for y in x])
        for x in test_text.combs])
    repeater = 0
    add = ''
    repeat = []
    # a = np.array([0] * (test_text.basetext[-1].word + 1))
    full_pwr = 0
    phonosyl_cont = 0
    for syllabs, x in repeats.items():
        syllabs = ''.join(map(lambda x: x.upper(), syllabs))

        if x.count < 2:
            continue
        full_pwr += x.power[0]
        phonosyl_cont += x.count
        repeat.append(f'<div id="d{repeater}" class="repeat_line">\
            <div class="btn-group ">\
  <button type="button" class="btn highlight">\
    👁\
  </button>\
  <div class="dropdown-menu">\
    <a class="dropdown-item" style="background-color:yellow" onclick="h_show(this, 0)">Example</a>\
    <a class="dropdown-item" style="background-color:aqua" onclick="h_show(this, 1)">Example</a>\
    <a class="dropdown-item" style="background-color:pink" onclick="h_show(this, 2)">Example</a>\
    <a class="dropdown-item" style="font-weight:800" onclick="h_show(this, 3)">Example</a>\
    <a class="dropdown-item" style="font-style:italic" onclick="h_show(this, 4)">Example</a>\
    <a class="dropdown-item" style="text-decoration:underline" onclick="h_show(this, 5)">Example</a>\
    <a class="dropdown-item" style="outline:dotted 2px #673ab7" onclick="h_show(this, 6)">Example</a>\
    <a class="dropdown-item" style="background-image:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAFCAYAAACEhIafAAAAF0lEQVQYV2NgYPjfwMDA8N+YARn8NwYANtMD5IC7yyQAAAAASUVORK5CYII=)" onclick="h_show(this, 7)">Example</a>\
  </div>\
</div>\
                    Σ <span class="summ">{x.power[0]:.2f}</span>\
                    x̅ <span class="mean">{x.power[1]:3.0}</span>\
                    N <span class="count">{x.count}</span>{syllabs}<span class="allrep" ><span class="rep">')

                    # <span class="highlight btn-outline-primary"></span>\

        last = x.combs[0][0][0].number
        add = ''
        for i in range(len(x.combs)):
            vol_num = 0

            if i > 0:
                repeat.append(f'{add}</span><span class="rep">')
                add = ''
                last = x.combs[i][0][0].number

            for y in x.combs[i][0]:
                if y.is_volve:
                    vol_num += 1
                    if vol_num > 1:
                        add += ')'
                        repeat.append('(')
                # if y.number < last:
                #     continue
                while last < y.number:
                    if test_text.basetext[last].origin != ' ':
                        repeat.append('-')
                    else:
                        repeat.append('|')
                    last += 1
                repeat.append(f"<span class=l{y.number}>{y.printable}</span>")
                last += 1
        repeat.append(f'{add}</span></span></div>')
        add = ''
        repeater += 1
    if repeater == 0:
        repeat = "В тексте не найдены повторы, соответствующие заданным фильтрам"
    repeat = re.sub(r'\|+', "|", ''.join(repeat))
    repeat = re.sub(r'-*\|*\)', ")", repeat)
    plt.clf()
    plt.cla()
    img = BytesIO()

    # a = gaussian_filter1d(a, sigma=3)
    # x = [0]
    # y = [a[0]]
    # for i in range(1, len(a)):
    #     if a[i] != a[i - 1]:
    #         x.append(i)
    #         y.append(a[i])

    a = [0] * (test_text.basetext[-1].syll + 1)
    b = [0] * (test_text.basetext[-1].word + 1)
    for rep in test_text.repeats.values():
        tmp = list(rep.letters.keys())
        for i in range(len(tmp) - 1):
            for j in range(1, len(tmp)):
                pwr = get_pwr(test_text.basetext[tmp[i]], test_text.basetext[tmp[j]])
                a[test_text.basetext[tmp[i]].syll] += pwr
                a[test_text.basetext[tmp[j]].syll] += pwr
                b[test_text.basetext[tmp[i]].word] += pwr
                b[test_text.basetext[tmp[j]].word] += pwr

    # a = gaussian_filter1d(a, sigma=2)
    # fs = fft(a)
    # max_pos = 0
    # for j, data in enumerate(fs):
    #     if abs(data) * (j + 1) > abs(fs[max_pos]) * (max_pos + 1):
    #         max_pos = j
    # max_pos /= len(fs)

    # g = [fs[j] * FH(abs(fs[j]) * len(fs) / (j + 1) - 3 * len(fs)) for j in np.arange(0, len(fs), 1)]
    # a3 = ifft(g)

    # fs = fft(b)
    # max_pos_w = 0
    # for j, data in enumerate(fs):
    #     if abs(data) * (j + 1) > abs(fs[max_pos_w]) * (max_pos + 1):
    #         max_pos_w = j
    # max_pos_w /= len(fs)

    # g = [fs[j] * FH(abs(fs[j]) * len(fs) / (j + 1) - 3 * len(fs)) for j in np.arange(0, len(fs), 1)]
    # b3 = ifft(g)

    plt.clf()
    plt.cla()
    plt.figure(figsize=[11, 8])
    plt.title("")
    tmp = plt.subplot(2, 1, 1)
    tmp.plot(a, 'o-')
    tmp.grid()
    # tmp.set_xticklabels([])
    tmp.set_title("Фоносиллабическая сила слогов (SPmax)")
    # tmp = plt.subplot(2, 2, 3)
    # tmp.plot(a3)
    # tmp.set_title("Отфильтрованные графики")

    tmp = plt.subplot(2, 1, 2)
    tmp.plot(b, 'o-')
    tmp.grid()
    # tmp.set_xticklabels([])
    tmp.set_title("Фоносиллабическая сила слов")

    # tmp = plt.subplot(2, 2, 4)
    # tmp.plot(b3)

    corr = pearsonr([a[i * len(a) // len(b)].real for i in range(len(b))], [a.real for a in b])
    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format="svg", transparent=True, dpi=300)

    img = f'<div style="">Количество цепочек повторов: {repeater}<br/>\
            Количество слогов: {len(test_text.SP)}<br/>\
            Количество слов: {test_text.basetext[-1].word}<br/>\
            Общая сила повторов: {full_pwr:.2f}<br/>\
            Средняя сила слога: ' + "{0:.2f}".format(full_pwr / (len(test_text.SP) + 1)) + f'<br/>\
            Средняя сила фоносиллаба: ' + "{0:.2f}".format(full_pwr / (phonosyl_cont + 1)) + f'<br/>\
            Средняя сила слова: ' + "{0:.2f}".format(full_pwr / test_text.basetext[-1].word) + f'<br/>\
            Корреляция фоноповторов слов и слогов:<br/> {corr[0]:.3f}, {corr[1]:.3f}\
            </div>' + re.sub(r'<style[^<]*</style>','',re.sub(r'(font-[^;]*;|\n\s*)', r'', img.getvalue().decode("utf8")))
    if request.args['lng'] == "rus":
        return render_template('mikl/result.html', filter=(filter_min, filter_max), base_text=request.form['text'], text=txt, spmax=spmax, comb=comb, repeat=repeat, img=img)
    return render_template('mikl/result_eng.html', filter=(filter_min, filter_max), base_text=request.form['text'], text=txt, spmax=spmax, comb=comb, repeat=repeat, img=img)


@BP.route('/statistic', methods=('GET', 'POST'))
def stat():
    if request.method != 'POST':
        return 'ERROR'
    out_type = request.form.get('simple', '0')

    repeats, test_text, filter_min, filter_max = calc_request(request)

    code = f'''Текст
------
{request.form['text']}
------
Фильтр ИАС-1: {request.form['filter']}
------
'''
    txt = repr(test_text.basetext)

    repeater = 0
    add = []
    repeat = ['Картина повторов\n------\n\n']
    repeat1 = []
    full_pwr = 0
    phonosyl_cont = 0
    for symbs, x in repeats.items():
        if x.count < 2:
            continue
        phonosyl_cont += x.count
        full_pwr += x.power[0]
        repeat.append(''.join(map(lambda x: x.upper(), symbs)))
        repeat.append(f':{repeater}[{x.count}; {x.power[0]:2.2f}; {x.power[1]:2.2f}]')
        repeat1.append(f'{repeater}:')
        tmp = list(x.letters.keys())
        tmp.sort()
        i = test_text.basetext[tmp[0]].syll
        last = tmp[0]
        volv_count = 0
        for y in tmp:
            if test_text.basetext[y].syll > i + 1:
                repeat.append(f'{add};')
                repeat1.append(f'{add};')
                add = []
                last = y
                volv_count = 0
            if test_text.basetext[y].is_volve:
                volv_count += 1
                if volv_count > 1:
                    repeat.append('(')
                    repeat1.append('(')
                    add.append(')')
            while last < y:
                if test_text.basetext[last].origin != ' ':
                    repeat.append('-')
                else:
                    # print('==', test_text.basetext[y].syll)
                    repeat.append('|')
                last += 1
            i = test_text.basetext[y - 1].syll
            repeat.append(f"{test_text.basetext[y].printable}")
            repeat1.append(f"{test_text.basetext[y].number},")
            last += 1
        repeat.extend(add)
        repeat.append('\n')
        repeat1.extend(add)
        repeat1.append('\n' + ';'.join(map(lambda t: ''.join(map(str, t[0])), x.combs)) + '\n')
        add = []
        repeater += 1
    if repeater == 0:
        repeat = "В тексте не найдены повторы, соответствующие заданным фильтрам"

    a = [0] * (test_text.basetext[-1].syll + 1)
    b = [0] * (test_text.basetext[-1].word + 1)
    for rep in test_text.repeats.values():
        tmp = list(rep.letters.keys())
        for i in range(len(tmp) - 1):
            for j in range(1, len(tmp)):
                pwr = get_pwr(test_text.basetext[tmp[i]], test_text.basetext[tmp[j]])
                a[test_text.basetext[tmp[i]].syll] += pwr
                a[test_text.basetext[tmp[j]].syll] += pwr
                b[test_text.basetext[tmp[i]].word] += pwr
                b[test_text.basetext[tmp[j]].word] += pwr

    a = gaussian_filter1d(a, sigma=2)
    fs = fft(a)
    max_pos = 0
    for j in range(len(fs)):
        if abs(fs[j]) * (j + 1) > abs(fs[max_pos]) * (max_pos + 1):
            max_pos = j
    max_pos /= len(fs)

    g = [fs[j] * FH(abs(fs[j]) * len(fs) / (j + 1) - 3 * len(fs)) for j in np.arange(0, len(fs), 1)]
    a3 = ifft(g)

    fs = fft(b)
    max_pos_w = 0
    for j in range(len(fs)):
        if abs(fs[j]) * (j + 1) > abs(fs[max_pos_w]) * (max_pos + 1):
            max_pos_w = j
    max_pos_w /= len(fs)

    g = [fs[j] * FH(abs(fs[j]) * len(fs) / (j + 1) - 3 * len(fs)) for j in np.arange(0, len(fs), 1)]
    b3 = ifft(g)


    corr = pearsonr([a3[i * len(a3) // len(b3)].real for i in range(len(b3))], [a.real for a in b3])


    count_volves, count_symbols = test_text.count_letters()

    add_text = f'''
Количество цепочек повторов          : {repeater}
Количество слогов                    : {len(test_text.SP)}
Количество слов                      : {test_text.basetext[-1].word}
Общая сила повторов                  : {full_pwr:.2f}
Средняя сила слога                   : {(full_pwr / (len(test_text.SP) + 1)):.2f}
Средняя сила фоносиллаба             : {(full_pwr / (phonosyl_cont + 1)):.2f}
Средняя сила слова                   : {(full_pwr / test_text.basetext[-1].word):.2f}
Корреляция фоноповторов слов и слогов: {corr[0]:.3f}, {corr[1]:.3f}
Количество звуков                    : {count_symbols}
'''

    if out_type == '1':
        return Response(''.join(repeat) + '\n' + ''.join(repeat1), mimetype='text/txt')
    elif out_type == 'csv':
        result = '"' + '";"'.join(map(str, (
            repeater,
            len(test_text.SP),
            test_text.basetext[-1].word,
            full_pwr,
            full_pwr / (len(test_text.SP) + 1),
            full_pwr / (phonosyl_cont + 1),
            full_pwr / test_text.basetext[-1].word,
            corr[0],
            corr[1],
            count_symbols,
        ))) + '"'
        return Response(result, mimetype='text/txt')

    result = ''.join(map(str, (
        code,
        add_text,
        ''.join(repeat),
        '\n',
        ''.join(repeat1),
        '''
-----------------------

 Техническй вид текста

-----------------------

''',
        txt
    )))

    return Response(result, mimetype='text/txt')


@BP.route('/svg', methods=('GET', 'POST'))
def svg():
    def FH(x):  # ступенчатая функция Хэвисайда
        if x >= 0:
            q = 1
        else:
            q = 0
        return q

    def get_pwr(a, b):
        pwr = 0
        mul = 1
        dist = b.syll - a.syll
        dist_w = b.word - a.word
        if 1 < dist < 50:
            pwr = 1 / dist / dist + 1 / max(1, dist_w) / max(1, dist_w)
            if a.origin == b.origin:
                mul += 1
            if a.w_pos[0] == b.w_pos[0]:
                mul += 1
            if a.w_pos[1] == b.w_pos[1]:
                mul += 1
            return pwr * mul * 2 / (b.w_pos[0] - b.w_pos[1] + a.w_pos[0] - a.w_pos[1])
        return 0

    if request.method != 'POST':
        return 'ERROR'
    out_type = request.form.get('simple', '0')

    repeats, test_text, filter_min, filter_max, filter_r_min, filter_r_max = calc_request(request)

    code = 'Текст\n------\n\n' + request.form['text'] + '\n------\nФильтры\n-------\n ИАС-1: ' + request.form['filter'] + '\n Сумма: ' + request.form['filter_r'] + '\n------\n'

    a = [0] * (test_text.basetext[-1].syll + 1)
    b = [0] * (test_text.basetext[-1].word + 1)
    for rep in test_text.repeats.values():
        tmp = list(rep.letters.keys())
        for i in range(len(tmp) - 1):
            for j in range(1, len(tmp)):
                pwr = get_pwr(test_text.basetext[tmp[i]], test_text.basetext[tmp[j]])
                a[test_text.basetext[tmp[i]].syll] += pwr
                a[test_text.basetext[tmp[j]].syll] += pwr
                b[test_text.basetext[tmp[i]].word] += pwr
                b[test_text.basetext[tmp[j]].word] += pwr

    a = gaussian_filter1d(a, sigma=2)
    # b = gaussian_filter1d(b, sigma=1)

    fs = fft(a)
    # g = [fs[j]*FH(abs(fs[j]) - 50) for j in np.arange(0, len(fs), 1)]
    # a1 = ifft(g)
    # g = [fs[j]*FH(50 - abs(fs[j])) for j in np.arange(0, len(fs), 1)]
    # a2 = ifft(g)
    g = [fs[j] * FH(abs(fs[j]) * len(fs) / (j + 1) - 3 * len(fs)) for j in np.arange(0, len(fs), 1)]
    a3 = ifft(g)

    fs = fft(b)
    # g = [fs[j]*FH(abs(fs[j]) - 50) for j in np.arange(0, len(fs), 1)]
    # b1 = ifft(g)
    # g = [fs[j]*FH(50 - abs(fs[j])) for j in np.arange(0, len(fs), 1)]
    # b2 = ifft(g)
    g = [fs[j] * FH(abs(fs[j]) * len(fs) / (j + 1) - 3 * len(fs)) for j in np.arange(0, len(fs), 1)]
    b3 = ifft(g)

    plt.clf()
    plt.cla()
    plt.figure(figsize=[11, 8])
    plt.title("Связность текста")
    tmp = plt.subplot(2, 2, 1)
    tmp.plot(a)
    tmp.set_xticklabels([])
    tmp.set_title("слоги")
    # tmp = plt.subplot(4, 2, 3)
    # tmp.plot(a1)
    # tmp.set_xticklabels([])
    # tmp.set_title("повторы большой амплитуды")
    # tmp = plt.subplot(4, 2, 5)
    # tmp.plot(a2)
    # tmp.set_xticklabels([])
    # tmp.set_title("повторы малой амплитуды")
    tmp = plt.subplot(2, 2, 3)
    tmp.plot(a3)
    tmp.set_title("Фильтрованный график")

    tmp = plt.subplot(2, 2, 2)
    tmp.plot(b)
    tmp.set_xticklabels([])
    tmp.set_title("слова")
    # tmp = plt.subplot(4, 2, 4)
    # tmp.plot(b1)
    # tmp.set_xticklabels([])
    # tmp = plt.subplot(4, 2, 6)
    # tmp.plot(b2)
    # tmp.set_xticklabels([])
    tmp = plt.subplot(2, 2, 4)
    tmp.plot(b3)

    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format="svg", transparent=True, dpi=300)
    return re.sub(r'<style[^<]*</style>','',re.sub(r'(font-[^;]*;|\n\s*)', r'', img.getvalue().decode("utf8")))
