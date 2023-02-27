# -*- coding: utf-8 -*-
"""
Quiz flask blueprint
"""

import re
import yaml
import os
import time
import hashlib
from pathlib import Path
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, Response, session
)
from app.mod.quiz_factory import Quiz
from app.auth import login_required
from random import randint

global blueprints_types
BP = Blueprint('quiz', __name__, subdomain='db') if os.environ.get('BLUEPRINTS_TYPES', "domains") == "domains" else Blueprint('quiz', __name__, url_prefix='/db')

def init_app(app):
    ''' During app initialization'''
    app.quizes_list = {}
    for quiz in os.listdir(app.config['QUIZESBASE']):
        tmp_quiz = Quiz()
        app.quizes_list[quiz] = tmp_quiz
        tmp_quiz.setup(path=os.path.join(app.config['QUIZESBASE'], quiz))
        tmp_quiz.load()


@BP.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    g.url_prefix = 'quiz'


@BP.route("/", methods=["GET", "POST"])
@BP.route("/list", methods=["GET", "POST"])
@login_required
def list():
    """
    Draw list of quizes
    """
    return render_template("quiz/base.html", list=current_app.quizes_list)


@BP.route("/quiz/<quiz_id>", methods=["GET", "POST"])
@login_required
def quiz_page(quiz_id=None):
    """
    Work with quiz <quiz_id>
    """
    if quiz_id is None:
        return redirect(url_for('quiz.list'))
    if quiz_id == "new":
        if request.method == "POST":

            new_quiz = yaml.load(request.form["text"])

            quizname = hashlib.md5(time.strftime("%y%m%d%H%M%S").encode()).hexdigest()
            # while quizname in current_app.quizes_list:
            #     quizname = hashlib.md5(time.strftime("%y%m%d%H%M%S").encode()).hexdigest()

            os.makedirs(os.path.join(current_app.config['QUIZESBASE'], quizname))

            new_quiz.setup(path=os.path.join(current_app.config['QUIZESBASE'], quizname))
            new_quiz.build_db()
            new_quiz.build_html()

            current_app.quizes_list[quizname] = new_quiz

            return redirect(url_for('quiz.list'))
        else:
            return render_template("quiz/new.html", name='return quiz_id')
    else:
        if quiz_id in current_app.quizes_list:
            quiz = current_app.quizes_list[quiz_id]
            if request.method == "POST":
                # flash(request.form)
                field_names = []
                values = []
                db = current_app.quizes_list[quiz_id].get_db()
                cursor = db.cursor()
                for field in request.form:
                    if field[0] == 'n':
                        continue
                    if quiz.form[int(field[5:])].__class__ is quiz.builder.Text:
                        filename = str(g.user.config['id']) + time.strftime("%y%m%d%H%M%S")
                        # flash(filename)
                        file = open(os.path.join(quiz.get_path(), filename), "w")
                        file.write(request.form.getlist(field)[0])
                        file.close()
                        values.append(filename)
                        field_names.append(field)
                        continue

                    res = []
                    for value in request.form.getlist(field):
                        if len(value) > 1 and value[0] == 'n':
                            tmp = request.form.getlist(value)[0]
                            # flash('INSERT INTO ' + field + ' (value) VALUES ("' + tmp + '");')
                            # flash('SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                            # print(' >>> SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                            cursor.execute('SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                            data = cursor.fetchone()
                            # flash(data)
                            if data is None:
                                # print(' >>> INSERT INTO ' + field + ' (value) VALUES ("' + tmp + '");')
                                # print(' >>> SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                                cursor.execute('INSERT INTO ' + field + ' (value) VALUES ("' + tmp + '");')
                                cursor.execute('SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                                data = cursor.fetchone()
                            res.append(str(data[0]))
                            quiz.form[int(field[5:])].values[data[0]] = tmp
                            quiz.build_html()
                        else:
                            res.append(value.replace('"', '""'))
                    values.append(','.join(res))
                    field_names.append(field)

                tmp = 'INSERT into question ( user, ' + ', '.join(field_names) + ') VALUES (' + str(g.user.config['id']) + ', "' + '", "'.join(values) + '")'
                # flash(tmp)
                # print(f' >>> {tmp}')
                cursor.execute(tmp)
                db.commit()
                db.close()
                flash(f'Запись {request.form["field0"]} добавлена в базу данных')

        return render_template("quiz/form.html", form=current_app.quizes_list[quiz_id].get_html())


@BP.route("/browse/", methods=["GET", "POST"])
@BP.route("/browse/<quiz_id>", methods=["GET", "POST"])
@login_required
def browse(quiz_id=None):
    """
    list of quizes result
    """
    if not g.user or quiz_id is None:
        return render_template('quiz/base.html', user=None)

    db = current_app.quizes_list[quiz_id].get_db()
    # print(' >>> SELECT * from structure')
    headers = db.execute('SELECT * from structure').fetchall()
    # flash(headers)
    where = ""
    sql = 'SELECT * FROM question '
    cnt = 'SELECT count(*) FROM question '
    if request.method == 'POST':
        where = request.form["where"]
        if where == '':
            where = '1'
        session['where'] = where

    sql += 'WHERE ' + session.get('where', '1').replace(';', '')
    cnt += 'WHERE ' + session.get('where', '1').replace(';', '')

    # flash(sql + ' LIMIT 30')
    # print(' >>> ' + sql + ' LIMIT 30')
    try:
        rows = db.execute(
            sql + ' LIMIT 100'
        ).fetchall()
    except Exception:
        session['where'] = '1'
        flash("Ошибка в запросе")
        return redirect(url_for('quiz.browse', quiz_id=quiz_id))
    cnt = db.execute(cnt).fetchone()[0]

    helps = []
    for el in current_app.quizes_list[quiz_id].form:
        helps.append(repr(el))

    # for row in rows:
    #     for i in range(2, len(row)):
    #         if 'values' in dir(current_app.quizes_list[quiz_id].form[i - 2]):
    #             row[i] = ', '.join(map(lambda x: current_app.quizes_list[quiz_id].form[i - 2].values[int(x)] if x!='' else '', row[i].split(',')))

    # flash(rows)

    return render_template('quiz/browse.html', rows=rows, headers=headers, request=session.get('where', ''), qid=quiz_id, forms=helps, count=cnt)

@BP.route("/dump_view/", methods=["GET", "POST"])
@BP.route("/dump_view/<int:N>", methods=["GET", "POST"])
def dump(N=0):
    """
    list of quizes result
    """
    quiz_id = '52e8fe1ac58dc6be0cfa3c1f129aab57'
    db = current_app.quizes_list[quiz_id].get_db()
    headers = db.execute('SELECT * from structure').fetchall()
    where = ""
    word = ""
    sql = 'SELECT * FROM question '
    cnt = 'SELECT count(*) FROM question '

    if request.method == 'POST':
        word = request.form["word"]
        where = request.form["where"]

    if where == '':
        where = '1'

    sql += 'WHERE ' + where.replace(';', '')
    cnt += 'WHERE ' + where.replace(';', '')

    if word == '':
        try:
            print(sql + f' LIMIT 100 OFFSET {100*N}')
            rows = db.execute(
                sql + f' LIMIT 100 OFFSET {100*N}'
            ).fetchall()
        except Exception:
            flash("Ошибка в запросе")
            return redirect(url_for('quiz.dump', N=0))
        cnt = db.execute(cnt).fetchone()[0]
    else:
        rows = []
        for row in db.execute(sql):
            filename = Path(os.path.join(current_app.quizes_list[quiz_id].get_path(), row[8]))
            if filename.is_file():
                with open(filename, "r", encoding="utf8") as f:
                    if f.read().lower().find(word) > -1:
                        rows.append(row)
            else:
                print(filename)
            if len(rows) == 10:
                break;
        cnt = 1

    routes = []
    if N == 0:
        routes.append((0, 'Первая', 1))
    else:
        routes.append((0, 'Первая'))

    start = max(min(N, cnt // 100 - 3) - 3, 0)
    end = min(start + 7, cnt // 100)

    for i in range(start, end):
        if i == N:
            routes.append((i, f'{i + 1} из {cnt // 100 + 1}', 1))
        else:
            routes.append((i, f'{i + 1} из {cnt // 100 + 1}'))

    if N == cnt // 100:
        routes.append((cnt // 100, 'Последняя', 1))
    else:
        routes.append((cnt // 100, 'Последняя'))

    helps = []
    for el in current_app.quizes_list[quiz_id].form:
        helps.append(repr(el))

    return render_template('quiz/dump.html', rows=rows, headers=headers, count=cnt, routes=routes, forms=helps, word=word, where=where)


@BP.route("/details/", methods=["GET", "POST"])
@BP.route("/details/<quiz_id>/<N>", methods=["GET", "POST"])
@BP.route("/details/<quiz_id>/<N>/<sub>", methods=["GET", "POST"])
def details(quiz_id=None, N=0, sub=None):
    if quiz_id is None:
        return render_template('quiz/base.html', user=None)

    db = current_app.quizes_list[quiz_id].get_db()
    sql = f'SELECT * FROM question WHERE N={N}'

    rows = db.execute(sql).fetchone()

    lst = {}
    for i in range(len(current_app.quizes_list[quiz_id].form)):
        if current_app.quizes_list[quiz_id].form[i].__class__.__name__ in ('Select', 'Choise'):
            lst[current_app.quizes_list[quiz_id].form[i].title] = ''
            if rows[i + 2] is None:
                lst[current_app.quizes_list[quiz_id].form[i].title] = ' None (Не задан) '
                continue
            for a in rows[i + 2].split(','):
                if a != '':
                    lst[current_app.quizes_list[quiz_id].form[i].title] += ' ' + current_app.quizes_list[quiz_id].form[i].values[int(a)]
        else:
            lst[current_app.quizes_list[quiz_id].form[i].title] = rows[i + 2]

        if rows[i + 2] is not None and re.search(r'[/\s\\]', rows[i + 2]) is None:
            my_file = Path(os.path.join(current_app.quizes_list[quiz_id].get_path(), rows[i + 2]))
            if my_file.is_file():
                if sub == "text":
                    return Response(open(my_file, 'r').read(), mimetype='text/txt')
                if request.args.get('get___txt', '0') == '1':
                    lst[current_app.quizes_list[quiz_id].form[i].title] = open(my_file, 'r').read()

    if request.args.get('get___txt', '0') == '1':
        return Response(repr(lst), mimetype='text/text')

    return render_template('quiz/details.html', list=lst)


@BP.route("/ans_edit/", methods=["GET", "POST"])
@BP.route("/ans_edit/<quiz_id>", methods=["GET", "POST"])
@BP.route("/ans_edit/<quiz_id>/<N>", methods=["GET", "POST"])
@login_required
def ans_edit(quiz_id=None, N=None):
    quiz = current_app.quizes_list[quiz_id]
    db = quiz.get_db()
    cursor = db.cursor()

    # if 'data' not in dir(ans_edit):
    #     ans_edit.data = {}
    # if quiz_id not in ans_edit.data:
    #     indexes = db.execute('SELECT N from question WHERE NOT EXISTS (SELECT N FROM checked WHERE question.N = checked.N)').fetchall()
    #     ans_edit.data[quiz_id] = {id_s[0] for id_s in indexes}

    if request.method == "POST" and g.user.is_expert:
        # flash(request.form)
        field_names = []
        values = []

        for field in request.form:
            if field[0] == 'n':
                continue
            if quiz.form[int(field[5:])].__class__ is quiz.builder.Text:
                filename = db.execute(f'SELECT {field} from question where N={N};').fetchone()[0]
                # filename = str(g.user.config['id']) + time.strftime("%y%m%d%H%M%S")
                # flash(filename)
                file = open(os.path.join(quiz.get_path(), filename), "w")
                file.write(request.form.getlist(field)[0])
                file.close()
                values.append(filename)
                field_names.append(field)
                continue

            res = []
            for value in request.form.getlist(field):

                if len(value) > 1 and value[0] == 'n':
                    tmp = request.form.getlist(value)[0]
                    # flash('INSERT INTO ' + field + ' (value) VALUES ("' + tmp + '");')
                    # flash('SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                    # print(' >>> SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                    cursor.execute('SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                    data = cursor.fetchone()
                    # flash(data)
                    if data is None:
                        # print(' >>> INSERT INTO ' + field + ' (value) VALUES ("' + tmp + '");')
                        # print(' >>> SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                        cursor.execute('INSERT INTO ' + field + ' (value) VALUES ("' + tmp + '");')
                        cursor.execute('SELECT N FROM ' + field + ' WHERE value="' + tmp + '"')
                        data = cursor.fetchone()
                    res.append(str(data[0]))
                    quiz.form[int(field[5:])].values[data[0]] = tmp
                    quiz.build_html()
                else:
                    res.append(value.replace('"', '""'))

            values.append(','.join(res))
            field_names.append(field)

        # print(' >>> UPDATE question  SET ' + ', '.join([f'{i}="{j}"' for i, j in zip(field_names, values)]) + f' where N={N};')
        cursor.execute('UPDATE question  SET ' + ', '.join([f'{i}="{j}"' for i, j in zip(field_names[:-1], values[:-1])]) + f' where N={N};')
        try:
            cursor.execute(f'INSERT into checked values ({N})')
        except Exception:
            pass
        db.commit()
        db.close()
        flash(f'Запись изменена в базе данных')
        return redirect(url_for('quiz.browse', quiz_id=quiz_id))

    if N is None:
        N = db.execute(
            'SELECT N FROM question WHERE NOT EXISTS (SELECT N FROM checked WHERE question.N = checked.N) ORDER by RANDOM() LIMIT 1'
            ).fetchone()[0]
        return redirect(url_for('quiz.ans_edit', quiz_id=quiz_id, N=N))

    if not g.user or quiz_id is None:
        return render_template('quiz/base.html', user=None)

    db = current_app.quizes_list[quiz_id].get_db()
    sql = f'SELECT * FROM question WHERE N={N}'

    # flash(sql + ' LIMIT 30')
    # print(' >>> ' + sql + ' LIMIT 30')
    rows = db.execute(sql).fetchone()

    lst = {}
    for i in range(len(current_app.quizes_list[quiz_id].form)):
        if rows[i + 2] is not None:
            my_file = Path(os.path.join(current_app.quizes_list[quiz_id].get_path(), rows[i + 2]))
            if len(rows[i + 2]) < 20 and my_file.is_file():
                lst[current_app.quizes_list[quiz_id].form[i].name] = open(my_file, 'r').read().replace('\n', '\\n').replace('"', '\"')
                continue

        if current_app.quizes_list[quiz_id].form[i].__class__.__name__ in ('Select', 'Choise'):
            if rows[i + 2] is None:
                continue
            for a in rows[i + 2].split(','):
                if a != '':
                    # flash(a)
                    # flash(current_app.quizes_list[quiz_id].form[i].values)
                    lst[current_app.quizes_list[quiz_id].form[i].name + '][value=' + a] = a
        else:
            lst[current_app.quizes_list[quiz_id].form[i].name] = rows[i + 2]
    # flash(lst)
    # return render_template('quiz/details.html', list=lst)
    return render_template("quiz/form.html", form=current_app.quizes_list[quiz_id].get_html(), data=lst)


@BP.route("/stat")
def dbstat():

    quiz_id = "52e8fe1ac58dc6be0cfa3c1f129aab57"
    sql = ['select count(1) from question']
    for i in range(1, 7):
        sql.append(f'select count(1) from question where field7 like "%{i}%"')
    sql.append('select count(1) from question where EXISTS (SELECT N FROM checked WHERE question.N = checked.N)')

    labels = ['Всего текстов', 'Художественных', 'Религиозных', 'Научных', 'Идеологических', 'Официально-деловых', 'Разговорных', 'Проведена экспертная оценка']
    db = current_app.quizes_list[quiz_id].get_db()
    sql = {l: str(db.execute(x).fetchone()[0]) for l, x in zip(labels, sql)}
    return Response(repr(sql), mimetype='text/text')

