from io import BytesIO
import re
import numpy as np
import matplotlib.pyplot as plt
import os


def sigmoid(x: float):
    return 1 / (1 + np.exp(-x))


def inv_sigmoid(x: float):
    return np.log(x / (1 - x))


def get_color(x: float, quantiles):
    if x > quantiles[2]:
        c = "#22b14c"
    elif x > quantiles[1]:
        c = "#77951c"
    elif x > quantiles[0]:
        c = "#ff8040"
    else:
        c = "#f0444d"
    return c


def predict_word(word, corpus, model, scale=3, length=1, activation="softmax", norm=False):

    wv = corpus.get_word_vector(word, True)
    zero_wv = np.zeros(wv.shape)

    pred_ = (model.predict_proba(wv * length)[0])
    if norm:
        pred_ = inv_sigmoid(pred_)
        shift = inv_sigmoid(model.predict_proba(zero_wv)[0])
        pred_ = sigmoid(pred_ - shift)
    if activation == "softmax":
        pred_ = np.exp(scale * pred_) / np.sum(np.exp(scale * pred_))
    elif activation == "linear":
        pred_ = inv_sigmoid(pred_)
    elif activation == "sigmoid":
        pass
    else:
        raise ValueError("Actication must be one of 'linear', 'softmax' or 'sigmoid'")
    return pred_


def plot_word_stats(model, corpus,  word,
                    quantiles=None, scale=3, length=1,
                    title=None, lines=None, skip=0, activation="softmax", json_data=None):
    _img = BytesIO()

    if title is None:
        title=word
    if json_data is None:
        json_data = {}
    json_data[title] = dict()
    pred_ = predict_word(word, corpus, model, scale, length, activation)
    if quantiles is not None:
        colors = [get_color(i, q) for i, q in zip(pred_, quantiles)]
    else:
        colors = ["#004078" for _ in pred_]
    if lines is None:
        lines = list(range(1, len(pred_)+1))

    tmp = min(len(lines), len(pred_)) - skip
    pred_ = pred_[-tmp:]
    lines = lines[-tmp:]

    plt.figure(figsize=(6, .3 * len(lines)))

    if quantiles is None:
        plt.barh(lines, 2 * pred_ - 1, color=colors)
        plt.xlim((-1, 1))
    else:
        plt.barh(lines, pred_, color=colors)
        plt.xlim((0, 1))

    for name ,value in zip(lines, pred_):
        json_data[title][name] = value

    plt.title(title)
    plt.savefig(_img, format="svg", bbox_inches='tight', transparent=True)
    return re.sub(r'<style[^<]*</style>','',re.sub(r'(font-[^;]*;|\n\s*)', r'',_img.getvalue().decode("utf8")))


def get_word_stats(model, corpus,  word,
                    quantiles=None, scale=3, length=1,
                    title=None, lines=None, skip=0, activation="softmax"):

    res_data = {}

    pred_ = predict_word(word, corpus, model, scale, length, activation)

    if lines is None:
        lines = list(range(1, len(pred_)+1))

    tmp = min(len(lines), len(pred_)) - skip
    pred_ = pred_[-tmp:]
    lines = lines[-tmp:]

    for name ,value in zip(lines, pred_):
        res_data[name] = value

    return res_data


def get_cos_color(x):
    if np.isnan(x):
        return f"0,0,0"
    return f"{255-(250*x)},0,{int(250*x)}"


def get_tan_color(x):
    if np.isnan(x):
        return f"0,0,0"

    x = -1 if x < -1 else x
    x = 1 if x > 1 else x
    return f"{127-(127*x)},0,{127+(127*x)}"


def color_word(word, value, tgt):
    # tgt = np.exp(3*tgt)/np.sum(np.exp(3*tgt))

    return (f"<span style='--main-color:rgb({get_cos_color(value)});"
            f"--color-a:rgb({get_tan_color(tgt[0])});"
            f"--color-b:rgb({get_tan_color(tgt[1])});"
            f"--color-c:rgb({get_tan_color(tgt[2])});"
            f"--color-d:rgb({get_tan_color(tgt[3])});"
            f"--color-e:rgb({get_tan_color(tgt[4])});"
            f"--color-f:rgb({get_tan_color(tgt[5])});"
            f"--color-g:rgb({get_tan_color(max(tgt[:-1]))});"
            f"'>{word}</span>"
            )


def color_text(colors):
    ''' return html colored text '''
    source = ' '.join([color_word(w, c, tgt) for w, c, tgt in colors])
    return f'<div id="color_text">{source}</div>'


def predict_word_hist(word, models, indises_x, indices_y, scale=3, length=1, title=None):
    keys = sorted(models.keys())
    res = []
    if title is None:
        title=word
    for i in keys:
        res_ = np.zeros(len(indices_y))-100
        model_ = models[i][0]
        corpus_ = models[i][1]

        wv = corpus_.get_word_vector(word, True)
        zero_wv = np.zeros(wv.shape)

        pred_ = (model_.predict_proba(wv*length)[0])
        for idx, value in zip(model_.classes_-1, pred_):
            res_[idx] = value

        res_ = np.exp(scale*res_) / np.sum(np.exp(scale*res_))

        res_ = np.cumsum(res_[::-1])[::-1]
        res.append(res_)
    idx_ = [indises_x[i] for i in keys]

    fig, ax = plt.subplots()
    for i, row in enumerate(zip(*res)):
        ax.bar(keys, row, label=indices_y[i+1], width=1)

    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
    plt.title(title)
    plt.xticks(keys, idx_)
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=45, horizontalalignment='right')

    _img = BytesIO()
    plt.savefig(_img, format="svg", bbox_inches='tight', transparent=True)
    return re.sub(r'(font-[^;]*;|\n\s*)', r'',_img.getvalue().decode("utf8"))


def b64unpack(str):
    import pickle as pkl
    import base64
    import gzip
    return pkl.loads(gzip.decompress(base64.b64decode(str)))


def get_word_imgs(word, structure, inv_dict, working_dir):

    try:
        wid = inv_dict[word.lower()]
        wfile = wid // 10000
        wnid = wid % 10000
    except:
        raise ValueError("No such word")
    imgs = []
    txt = ['<table id="sord_summary">']
    from io import BytesIO
    import base64, re
    struc = structure[1]
    s_keys = list(struc.keys())
    titles = ["Встречаемость",
              "Стиль",
              "Социально-сословная специфика\nОтсутствует — Присутствует",
              "Социально-возрастная специфика",
              "Профессиональная специфика\nОтсутствует — Присутствует",
              "Гендерная специфика",
              "Ксенологическая специфика\nОтсутствует — Присутствует",
              "Хронологическая специфика",
              "Стих — Проза",
              "Монолог — Диалог",
              "Паремия — Развёрнутый текст",
              "Эмоциональная оценка\nОтрицательная — Положительная",
              ]
    plt.rcParams['svg.fonttype'] = 'none'
    with open(os.path.join(working_dir, "coefs", f'{str(wfile)}.pkl')) as f:
        for i, s in enumerate(f):
            _, classes, coef = b64unpack(s[:-1])
            coef = np.array(coef[:, wnid])

            if i == 11:
                coef = -coef
            if i in (5, 7):
                coef = np.array([-coef[0], coef[0]])
            elif titles[i].find("—") == -1:
                if np.sum(np.abs(coef)) != 0:
                    coef = coef / np.sum(np.abs(coef))
            if titles[i][0] == '-':
                continue

            _img = BytesIO()
            plt.figure(figsize=(5, 0.3 * len(list(coef))))
            plt.title(titles[i])
            # plt.xlim(-1.1,1.1)
            # plt.xticks(np.arange(-1, 1.1, 0.2))
            _labels = dict(struc[s_keys[i]])

            try:
                labels = [_labels.get(j,"отсутствует") for j in classes]
            except:
                print(_labels, classes, "WTF?!", sep="\n")
            else:
                if titles[i].find("—") == -1:
                    if np.isnan(coef[0]):
                        txt.extend(['<tr><td>', titles[i], '</td><td>', 'отсутствует', '</td></tr>'])
                    else:
                        txt.extend(['<tr><td>', titles[i], '</td><td>', labels[np.argmax(coef)],'</td></tr>'])
                else:
                    txt.extend(['<tr><td>', titles[i], '</td><td>', titles[i].split('\n')[-1].replace('—', 'нейтральная').split(' ')[0 if coef[0] < -0.5 else (1 if coef[0] < 0.5 else 2)], '</td></tr>'])

                if titles[i].find("—") == -1:
                    if np.isnan(coef[0]):
                        plt.barh(labels, [0.01 for _ in coef])
                        plt.xlim((-1, 1))
                    else:
                        plt.barh(labels, list(coef))
                else:
                    plt.barh([""], list(coef))
                if titles[i].find("—") != -1:
                    plt.xlim((-1, 1))
            finally:
                plt.savefig(_img, format="svg", bbox_inches='tight', transparent=True)
                _img.seek(0)
                imgs.append(re.sub(r'<style[^<]*</style>','',re.sub(r'(font-[^;]*;|\n\s*)', r'',_img.getvalue().decode("utf8"))))
                # imgs.append(_img.getvalue().decode("utf8").replace("font-family:DejaVu Sans;font-size:10px;font-style:normal;font-weight:normal;",'').replace("\n",''))
                # imgs.append(base64.b64encode(_img.getvalue()).decode("utf8"))
                del coef
    txt = txt[0:1] + txt[6:]  # + txt[1:6]
    txt.append('</table>')
    imgs = imgs[1:] + [' '.join(txt)] + [imgs[0]]
    return imgs

def get_word_dict(word, structure, inv_dict, working_dir):

    try:
        wid = inv_dict[word.lower()]
        wfile = wid // 10000
        wnid = wid % 10000
    except:
        raise ValueError("No such word")
    import base64, re

    struc = structure[1]
    s_keys = list(struc.keys())
    titles = [
        "Встречаемость",
        "Стиль",
        "Социально-сословная специфика\nОтсутствует — Присутствует",
        "Социально-возрастная специфика",
        "Профессиональная специфика\nОтсутствует — Присутствует",
        "Гендерная специфика",
        "Ксенологическая специфика\nОтсутствует — Присутствует",
        "Хронологическая специфика",
        "Стих — Проза",
        "Монолог — Диалог",
        "Паремия — Развёрнутый текст",
        "Эмоциональная оценка\nОтрицательная — Положительная",
    ]

    id = [
        "time",
        "style",
        "estate",
        "age",
        "profession",
        "gender",
        "xenological",
        "chronologic",
        "verse",
        "monolog",
        "paremia",
        "emotional",
    ]

    res = {'results': [], 'word': word.lower()}

    with open(os.path.join(working_dir, "coefs", f'{str(wfile)}.pkl')) as f:
        for i, s in enumerate(f):
            _, classes, coef = b64unpack(s[:-1])

            coef = np.array(coef[:, wnid])
            if i == 11:
                coef = -coef
            if i in (5, 7):
                coef = np.array([-coef[0], coef[0]])
            elif titles[i].find("—") == -1:
                if np.sum(np.abs(coef)) != 0:
                    coef = coef / np.sum(np.abs(coef))
            if titles[i][0] == '-':
                continue

            _labels = dict(struc[s_keys[i]])
            labels = []
            for j in classes:
                if j not in _labels:
                    _labels[int(j)] = "отсутствует"
                labels.append(_labels[j])

            if titles[i].find("—") == -1:
                if np.isnan(coef[0]):
                    val = 'отсутствует', -1
                else:
                    val = labels[np.argmax(coef)], int(classes[np.argmax(coef)])
            else:
                if i == 11:
                    val = titles[i].split('\n')[-1].replace('—', 'нейтральная').split()[0 if coef[0] < -0.5 else (1 if coef[0] < 0.5 else 2)], max(-1,min(1,coef[0]))
                else:
                    val = titles[i].split('\n')[-1].replace('—', 'нейтральная').split()[0 if coef[0] < -0.5 else (1 if coef[0] < 0.5 else 2)], max(-1,min(1,coef[0]))

            if np.isnan(coef[0]):
                coef = [-100 for _ in coef]

            res['results'].append({
                'id': id[i],
                'title': titles[i].split('\n')[0],
                'original': list(coef),
                'value': val,
                'labels': _labels,
                'softmax': list(np.exp(3*coef)/np.sum(np.exp(3*coef))),
            })
            del coef
    return res