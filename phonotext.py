# -*- coding: utf-8 -*-
'''
Основной модуль
'''
# standart
import re
from os import path, environ
# flask
import flask
import flask_migrate
import flask_sqlalchemy
# own
from app.mod import filework, textwork, models
from app.db import get_db


PDB = models.PDB

BP = flask.Blueprint('phonotext', __name__, url_prefix='/base', subdomain='phonotext')  if environ.get('BLUEPRINTS_TYPES', "domains") == "domains" else flask.Blueprint('phonotext', __name__, url_prefix='/phonotext/base')

@BP.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    ''' Setup url_prefix'''
    flask.g.url_prefix = 'phonotext'

def init_app(app):
    """Register click command to app and setup SQLAlchemy"""

    PDB.init_app(app)
    BP.MIGRATE = flask_migrate.Migrate(app, PDB)

# Отображение страниц

@BP.route('/', methods=['GET', 'POST'])
@BP.route('/index', methods=['GET', 'POST'])
def index():
    '''
    Основная страница
    '''
    if not flask.g.user:
        return flask.render_template('phonotext/index.html')
    my_hist = my_history()
    all_hist = all_history()
    search_hist = None
    return flask.render_template('phonotext/index.html', my_history=my_hist, all_history=all_hist, search=search_hist)


@BP.route('/text/<int:analyze_id>')
def analyze(analyze_id: int):
    '''
    Страница отображения анализа
    '''
    analyzed_text = models.Analyze.query.filter_by(id=analyze_id).first_or_404()
    return flask.render_template('phonotext/edit.html', analyzed_text=analyzed_text)


@BP.route('/edit/<int:analyze_id>')
def edit_analyze(analyze_id: int):
    '''
    Страница изменения анализа
    '''
    analyzed_text = models.Analyze.query.filter_by(id=analyze_id).first_or_404()
    return flask.render_template('phonotext/edit.html', analyzed_text=analyzed_text)


@BP.route('/dict_edit')
def dict_edit():
    '''
    Страница отображения словарей
    '''
    return flask.render_template('phonotext/dict.html')


# Вспомогательные функции

def to_json(history):
    '''
    Преобразование объектов для ajax
    '''
    hist = []
    for item in history:
        fields = {}
        for field in [x for x in dir(item) if not x.startswith('_') and x != 'metadata']:
            data = item.__getattribute__(field)
            try:
                flask.json.dumps(data)
                fields[field] = data
            except TypeError:
                pass
        hist.append(fields)
    hist = flask.json.dumps(hist)
    return hist


@BP.route('/inter_analyze', methods=['GET', 'POST'])
@BP.route('/edit/inter_analyze', methods=['GET', 'POST'])
@BP.route('/text/inter_analyze', methods=['GET', 'POST'])
def inter_analyze():
    '''
    Ассинхронная обработка текста
    '''
    text = flask.request.form['text']
    cur_id = flask.request.form['cur_id']
    private = flask.request.form['private']
    author_name = flask.request.form['author_name']
    text_name = flask.request.form['text_name']
    text_series = flask.request.form['text_series']
    text_year = flask.request.form['text_year']
    cons1 = flask.request.form['cons1']
    cons2 = flask.request.form['cons2']
    cons3 = flask.request.form['cons3']
    comm1 = flask.request.form['comm1']
    comm2 = flask.request.form['comm2']
    ias1 = flask.request.form['ias1']
    ias2 = flask.request.form['ias2']
    ias3 = flask.request.form['ias3']
    lang = flask.request.form['lang']
    if len(text) < 10:
        return flask.json.dumps('err1')
    if len(text) > 10000:
        return flask.json.dumps('err2')
    if cur_id != 'interact':
        main = models.Analyze.query.filter_by(id=cur_id).first()
        accents = dict(main.custom_accents)
        analyzed_text = textwork.go_analyze(text, [[cons1, cons2, cons3], [comm1, comm2], [ias1, ias2, ias3]], lang, accents)
    else:
        analyzed_text = textwork.go_analyze(text, [[cons1, cons2, cons3], [comm1, comm2], [ias1, ias2, ias3]], lang)
    return flask.json.dumps(analyzed_text)


@BP.route('/search', methods=['GET', 'POST'])
def search():
    '''
    Отображение результатов поиска по существующим анализам
    '''
    search_text = flask.request.form['search']
    search_hist = search_result(search_text)
    return flask.json.dumps([to_json(search_hist[0]), list(search_hist[1]), search_hist[2], search_hist[3], search_hist[4]])


@BP.route('/doc/<path:doc_id>')
def doc_download(doc_id):
    '''
    Загрузка .docx
    '''
    return flask.send_from_directory('../archive/', doc_id + '.docx', as_attachment=True)


@BP.route('/txt/<path:txt_id>')
def txt_download(txt_id):
    '''
    Загрузка .txt
    '''
    return flask.send_from_directory('../archive/', txt_id + '.txt', as_attachment=True)


###############
# Работа с БД #
###############

# Работа с анализами

@BP.route('/interact/', methods=['GET', 'POST'])
def interact():
    '''
    Добавление анализа с главной страницы
    '''
    text = flask.request.form['text']
    lang = flask.request.form['lang']
    analyzed_text = textwork.go_analyze(text, [['true', 'true', 'true'], ['true', 'true'], [6, 6, 6]], lang)
    analyze_id = add_analyze(analyzed_text, ['true', None, None, None, None, ['true', 'true', 'true'], ['true', 'true'], [6, 6, 6], lang])
    return flask.json.dumps(analyze_id)


@BP.route('/start/<int:text_id>', methods=['GET', 'POST'])
@BP.route('/edit/start/<int:text_id>', methods=['GET', 'POST'])
def start(text_id):
    '''
    Добавление анализа со страницы редактирования
    '''
    text = flask.request.form['text']
    private = flask.request.form['private']
    author_name = flask.request.form['author_name']
    text_name = flask.request.form['text_name']
    text_series = flask.request.form['text_series']
    text_year = flask.request.form['text_year']
    cons1 = flask.request.form['cons1']
    cons2 = flask.request.form['cons2']
    cons3 = flask.request.form['cons3']
    comm1 = flask.request.form['comm1']
    comm2 = flask.request.form['comm2']
    ias1 = flask.request.form['ias1']
    ias2 = flask.request.form['ias2']
    ias3 = flask.request.form['ias3']
    lang = flask.request.form['lang']
    if len(text) < 10:
        flask.flash('Слишком короткий текст.', 'text')
        return flask.redirect(flask.url_for('phonotext.index'))
    if len(text) > 1000:
        flask.flash('Слишком большой текст.', 'text')
        return flask.redirect(flask.url_for('phonotext.index'))
    if text_id and text_id != 0:
        main_custom = models.Analyze.query.filter_by(id=text_id).first()
        accents = dict(main_custom.custom_accents)
        analyzed_text = textwork.go_analyze(text, [[cons1, cons2, cons3], [comm1, comm2], [ias1, ias2, ias3]], lang, accents)
        analyze_id = update_analyze(analyzed_text, [private, author_name, text_name, text_series, text_year, [cons1, cons2, cons3], [comm1, comm2], [ias1, ias2, ias3], lang], text_id)
    else:
        analyzed_text = textwork.go_analyze(text, [[cons1, cons2, cons3], [comm1, comm2]], lang)
        analyze_id = add_analyze(analyzed_text, [private, author_name, text_name, text_series, text_year, [cons1, cons2, cons3], [comm1, comm2], lang])
    filework.txt_out(str(analyze_id), analyzed_text)
    filework.doc_out(str(analyze_id), analyzed_text)
    if analyzed_text['replaced']:
        flask.flash('Была произведена автозамена в словах: %s' % analyzed_text['replaced'], 'replaced_words')
    if text_id and text_id != 0:
        return flask.json.dumps(True)
    else:
        return flask.json.dumps(analyze_id)


def add_analyze(analyzed_text: dict, settings):
    '''
    Функция добавления анализа
    '''
    analyzed = models.Analyze(
        base_str=analyzed_text['base'],
        base=analyzed_text['lines'],
        syll=analyzed_text['syll'],
        comb=analyzed_text['comb'],
        vibr=analyzed_text['vibr'],
        repeat=analyzed_text['rep'],
        accents=analyzed_text['accents'],
        custom_accents=analyzed_text['custom'],
        temp=False,
        user_id=flask.g.user.config['id'],
        private=True if settings[0] == 'true' else False,
        author=settings[1],
        name=settings[2],
        series=settings[3],
        year=int(settings[4]) if settings[4] else None,
        settings=[settings[5], settings[6], settings[7], settings[8]])
    PDB.session.add(analyzed)
    PDB.session.commit()
    return analyzed.id


def update_analyze(analyzed_text: dict, settings, text_id: int):
    '''
    Функция изменения анализа
    '''
    old = models.Analyze.query.filter_by(id=text_id).first()
    old.base_str = analyzed_text['base']
    old.base = analyzed_text['lines']
    old.syll = analyzed_text['syll']
    old.comb = analyzed_text['comb']
    old.vibr = analyzed_text['vibr']
    old.repeat = analyzed_text['rep']
    old.accents = analyzed_text['accents']
    old.custom_accents = analyzed_text['custom']
    old.private = True if settings[0] == 'true' else False
    old.author = settings[1]
    old.name = settings[2]
    old.series = settings[3]
    old.year = int(settings[4]) if settings[4] else None
    old.settings = [settings[5], settings[6], settings[7], settings[8]]
    clone = PDB.session.merge(old)
    PDB.session.add(clone)
    PDB.session.commit()
    return old.id


@BP.route('/delete_analyze/<int:text_id>')
def delete_analyze(text_id: int):
    '''
    Функция удаления анализа
    '''
    local_res = models.Analyze.query.filter_by(id=text_id).first()
    merge_res = PDB.session.merge(local_res)
    PDB.session.delete(merge_res)
    PDB.session.commit()
    flask.flash('Анализ успешно удалён', 'main')
    return flask.redirect(flask.url_for('phonotext.index'))


# Работа со словарями ударений и замены

@BP.route('/dict_reload', methods=['GET', 'POST'])
def dict_reload():
    '''
    Возвращает словари
    '''
    mark = flask.request.form['mark']
    if mark == 'acc':
        accents = models.Accent.query.order_by(models.Accent.word).all()
        acc = []
        for item in accents:
            acc.append([item.word, item.accent, item.addit])
        return flask.json.dumps(acc)
    else:
        replace = models.Replace.query.order_by(models.Replace.word).all()
        rep = []
        for item in replace:
            rep.append(item.word)

        return flask.json.dumps(rep)


@BP.route('/edit/del_custom', methods=['GET', 'POST'])
def del_custom():
    '''
    Удаление местного акцента
    '''
    word = flask.request.form['word']
    word_pos = flask.request.form['word_pos']
    cur_id = flask.request.form['cur_id']
    main = models.Analyze.query.filter_by(id=cur_id).first()
    acc = main.custom_accents
    if acc:
        if word in acc:
            for pos in acc[word]:
                if pos[0] == word_pos:
                    acc[word].remove(pos)
    main.custom_accents = ''
    PDB.session.commit()
    main.custom_accents = acc
    PDB.session.commit()
    return flask.json.dumps(True)


@BP.route('/change_accent', methods=['GET', 'POST'])
@BP.route('/edit/change_accent', methods=['GET', 'POST'])
def change_accent():
    '''
    Изменение местного акцента
    '''
    word = flask.request.form['word']
    word_pos = flask.request.form['word_pos']
    vow_pos = flask.request.form['vow_pos']
    add_vow = flask.request.form['add_vow']
    cur_id = flask.request.form['cur_id']
    main = models.Analyze.query.filter_by(id=cur_id).first()
    acc = main.custom_accents
    if acc:
        if word in acc:
            for pos in acc[word]:
                if pos[0] == word_pos:
                    pos[1] = vow_pos
                    pos[2] = add_vow
                    break
            else:
                new_word_pos = [word_pos, vow_pos, add_vow]
                acc[word].append(new_word_pos)
        else:
            acc[word] = [[word_pos, vow_pos, add_vow]]
    else:
        acc = {word:[[word_pos, vow_pos, add_vow]]}
    main.custom_accents = ''
    PDB.session.commit()
    main.custom_accents = acc
    PDB.session.commit()
    return flask.json.dumps(True)


@BP.route('/dict_red', methods=['GET', 'POST'])
def dict_red():
    '''
    Функция добавления/удаления слова из словаря автозамены е->ё
    '''
    word = flask.request.form['word']
    mark = flask.request.form['mark']
    if '' == word:
        mess = 'Передана пустая строка.'
        return flask.json.dumps([True, '', mess])
    elif len(word) == 1:
        mess = 'Передан одиночный символ.'
        return flask.json.dumps([True, '', mess])
    elif 'ё' not in word and '?' not in word:
        mess = 'Слово должно содержать "ё".'
        return flask.json.dumps([True, '', mess])
    elif ' ' in word:
        mess = 'Только одно слово.'
        return flask.json.dumps([True, '', mess])
    if 'add' in mark:
        local_res = models.Replace.query.filter_by(word=word.replace('ё', '?')).first()
        if local_res:
            mess = 'Слово "%s" уже записано.' % word
        else:
            repl = models.Replace(word=word.replace('ё', '?'))
            PDB.session.add(repl)
            PDB.session.commit()
            mess = 'Успешно добавлено слово "%s".' % word
        return flask.json.dumps([True, 'add', mess])
    elif 'del' in mark:
        local_res = models.Replace.query.filter_by(word=word.replace('ё', '?')).first()
        if local_res:
            merge_res = PDB.session.merge(local_res)
            PDB.session.delete(merge_res)
            PDB.session.commit()
            mess = 'Успешно удалено слово "%s".' % word
        else:
            mess = 'Не найдено слово "%s".' % word
        return flask.json.dumps([True, 'del', mess])
    return flask.json.dumps(False)


@BP.route('/edit/accent_add', methods=['GET', 'POST'])
def accent_add():
    '''
    Добавление слова через режим интерактивного анализа
    '''
    word = flask.request.form['word'].lower()
    vow_pos = flask.request.form['vow_pos']
    add_vow = flask.request.form['add_vow']
    if add_vow == '':
        add_vow = None
    all = models.Accent.query.order_by(models.Accent.id.desc()).all()
    repl = models.Accent(word=word, accent=vow_pos, addit=add_vow)
    PDB.session.add(repl)
    PDB.session.commit()
    return flask.json.dumps(True)


@BP.route('/accent_red', methods=['GET', 'POST'])
def accent_red():
    '''
    Функция добавления/удаления слова из словаря ударений
    '''
    word = flask.request.form['word'].lower()
    mark = flask.request.form['mark']
    if '' == word:
        mess = 'Передана пустая строка.'
        return flask.json.dumps([True, '', mess])
    elif ' ' in word:
        mess = 'Только одно слово.'
        return flask.json.dumps([True, '', mess])
    elif re.findall(r'[^а-яёa-z-12]', word):
        mess = 'Присутствуют недопустимые символы. Допускаются только буквы, символ "-", пометки ударений "1" и "2".'
        return flask.json.dumps([True, '', mess])
    main = re.findall('1', word)
    if len(main) == 0:
        mess = 'Должно быть одно основное ударение, помеченное "1" перед гласной. Некорректный вариант: "околоземный"'
        return flask.json.dumps([True, '', mess])
    elif len(main) > 1:
        mess = 'Должна быть только одна пометка "1" на основное ударение перед гласной. Некорректный вариант: "1околоз11емный"'
        return flask.json.dumps([True, '', mess])
    add = re.findall('2', word)
    if len(add) > 1:
        mess = 'Должно быть не более одной пометки "2" на побочное ударение перед гласной. Некорректный вариант: "2ок2олоз1емный"'
        return flask.json.dumps([True, '', mess])
    main_accent = re.findall('1[аоуыиэюяеё]', word)
    if add:
        add_accent = re.findall('2[аоуыиэюяеё]', word)
        if len(main_accent) > 1:
            mess = 'Должно быть только одно побочное ударение, помеченное "2" перед гласной. Некорректный вариант: "2околоз2емный"'
            return flask.json.dumps([True, '', mess])
        main_pos = word.index(main_accent[0])
        add_pos = word.index(add_accent[0])
        if main_pos < add_pos:
            add_pos = add_pos - 1
        else:
            main_pos = main_pos - 1
        clear_word = re.sub('[12]', '', word)
        local_res = models.Accent.query.filter_by(word=clear_word, accent=main_pos, addit=add_pos).first()
        if 'add' in mark:
            if local_res:
                mess = 'Слово "%s" с основным ударением на %s-й символ ("%s") и побочным ударением на %s-й символ ("%s") уже записано.' % (clear_word, main_pos + 1, clear_word[main_pos:main_pos+1], add_pos + 1, clear_word[add_pos:add_pos+1])
            else:
                repl = models.Accent(word=clear_word, accent=main_pos, addit=add_pos)
                PDB.session.add(repl)
                PDB.session.commit()
                mess = 'Успешно добавлено слово "%s" с основным ударением на %s-й символ ("%s") и побочным ударением на %s-й символ ("%s").' % (clear_word, main_pos + 1, clear_word[main_pos:main_pos+1], add_pos + 1, clear_word[add_pos:add_pos+1])
            return flask.json.dumps([True, 'add', mess])
        elif 'del' in mark:
            if local_res:
                merge_res = PDB.session.merge(local_res)
                PDB.session.delete(merge_res)
                PDB.session.commit()
                mess = 'Успешно удалено слово "%s" с основным ударением на %s-й символ ("%s") и побочным ударением на %s-й символ ("%s").' % (clear_word, main_pos + 1, clear_word[main_pos:main_pos+1], add_pos + 1, clear_word[add_pos:add_pos+1])
            else:
                mess = 'Не найдено слово "%s" с основным ударением на %s-й символ ("%s") и побочным ударением на %s-й символ ("%s").' % (clear_word, main_pos + 1, clear_word[main_pos:main_pos+1], add_pos + 1, clear_word[add_pos:add_pos+1])
            return flask.json.dumps([True, 'del', mess])
    else:
        clear_word = re.sub('1', '', word)
        pos_vow = word.index(main_accent[0])
        local_res = models.Accent.query.filter_by(word=clear_word, accent=pos_vow, addit=None).first()
        if 'add' in mark:
            if local_res:
                mess = 'Слово "%s" с ударением на %s-й символ ("%s") уже записано.' % (clear_word, pos_vow + 1, clear_word[pos_vow:pos_vow+1])
            else:
                repl = models.Accent(word=clear_word, accent=pos_vow, addit=None)
                PDB.session.add(repl)
                PDB.session.commit()
                mess = 'Успешно добавлено слово "%s" с ударением на %s-й символ ("%s").' % (clear_word, pos_vow + 1, clear_word[pos_vow:pos_vow+1])
            return flask.json.dumps([True, 'add', mess])
        elif 'del' in mark:
            if local_res:
                merge_res = PDB.session.merge(local_res)
                PDB.session.delete(merge_res)
                PDB.session.commit()
                mess = 'Успешно удалено слово "%s" с ударением на %s-й символ ("%s").' % (clear_word, pos_vow + 1, clear_word[pos_vow:pos_vow+1])
            else:
                mess = 'Не найдено слово "%s" с ударением на %s-й символ ("%s").' % (clear_word, pos_vow + 1, clear_word[pos_vow:pos_vow+1])
            return flask.json.dumps([True, 'del', mess])
    return flask.json.dumps(False)


def dict_get():
    '''
    Получение словаря автозамены
    '''
    words: list = []
    repl = models.Replace.query.all()
    for word in repl:
        words.append(word.word)
    return words

def accent_get():
    '''
    Получение словаря ударений
    '''
    words: list = []
    repl = models.Accent.query.all()
    for word in repl:
        words.append([word.word, word.accent, word.addit])
    return words


# Выбор определённых анализов

def all_history(page=1):
    '''
    Пагинация общей истории анализов
    '''
    history = models.Analyze.query.filter(flask_sqlalchemy.sqlalchemy.and_(models.Analyze.user_id != flask.g.user.config['id'], models.Analyze.private == False)).order_by(models.Analyze.timestamp.desc()).paginate(page, 3, False)
    author_names = set()
    for item in history.items:
        user = flask.g.db.execute(f'SELECT username, id from user where id=:user_id', {'user_id': str(item.user_id)}).fetchone()
        if user:
            author_names.add((user[0], user[1]))
    if history.has_next:
        next_page = history.next_num
    else:
        next_page = None
    if history.has_prev:
        prev_page = history.prev_num
    else:
        prev_page = None
    return [history.items, author_names, next_page, prev_page]


def my_history(page=1):
    '''
    Пагинация личной истории анализов
    '''
    history = models.Analyze.query.filter_by(user_id=flask.g.user.config['id']).order_by(models.Analyze.timestamp.desc()).paginate(page, 3, False)
    author_names = set()
    for item in history.items:
        user = flask.g.db.execute(f'SELECT username, id from user where id=:user_id', {'user_id': str(item.user_id)}).fetchone()
        if user:
            author_names.add((user[0], user[1]))
    if history.has_next:
        next_page = history.next_num
    else:
        next_page = None
    if history.has_prev:
        prev_page = history.prev_num
    else:
        prev_page = None
    return [history.items, author_names, next_page, prev_page]


def search_result(search_text: str, page=1):
    '''
    Пагинация поиска по истории анализов
    '''
    history = models.Analyze.query.filter(models.Analyze.base_str.like('%' + str(search_text) + '%')).filter(flask_sqlalchemy.sqlalchemy.or_(models.Analyze.user_id == flask.g.user.config['id'], models.Analyze.private == True)).order_by(models.Analyze.timestamp.desc()).paginate(page, 4, False)
    author_names = set()
    for item in history.items:
        user = flask.g.db.execute(f'SELECT username, id from user where id=:user_id', {'user_id': str(item.user_id)}).fetchone()
        if user:
            author_names.add((user[0], user[1]))
    if history.has_next:
        next_page = history.next_num
    else:
        next_page = None
    if history.has_prev:
        prev_page = history.prev_num
    else:
        prev_page = None
    return [history.items, author_names, next_page, prev_page, search_text]


@BP.route('/paginate', methods=['GET', 'POST'])
def paginate():
    '''
    Общая функция пагинации
    '''
    field = flask.request.form['field']
    req = int(flask.request.form['req'])
    if field == 'all':
        addit = all_history(req)
        parsed = to_json(addit[0])
        return flask.json.dumps([parsed, list(addit[1]), addit[2], addit[3]])
    elif field == 'my':
        addit = my_history(req)
        parsed = to_json(addit[0])
        return flask.json.dumps([parsed, list(addit[1]), addit[2], addit[3]])
    elif field == 'search':
        search_hist = flask.request.form['search']
        addit = search_result(search_hist, req)
        parsed = to_json(addit[0])
        return flask.json.dumps([parsed, list(addit[1]), addit[2], addit[3], addit[4]])


if __name__ == '__main__':
    APP.run(debug=True)
