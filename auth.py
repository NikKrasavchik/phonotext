import functools
import random

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from subprocess import Popen, PIPE

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

class User:
    def __init__(self, config):
        self.config = config

    @property
    def is_admin(self):
        return self.config['accesslvl'] > 99

    @property
    def is_expert(self):
        return self.config['accesslvl'] > 49

    @property
    def is_activated(self):
        return self.config['accesslvl'] > -1

@bp.url_value_preprocessor
def bp_url_value_preprocessor(endpoint, values):
    g.url_prefix = 'auth'

def send_email(subject, html, email):
    """
    send html through email
    """

    # using mutt

    p = Popen(["mutt",
               "-F",
               "/home/mikl/lit_site/.muttrc",
               "-e",
               "set content_type=text/html",
               email,
               "-s",
               subject], stdin=PIPE)
    p.communicate(bytes(html, "utf-8"))


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if not g.user.is_activated:
            return redirect(url_for('auth.checkemail'))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        # g.user = get_db().execute(
        #     'SELECT * FROM user WHERE id = ?', (2,)
        # ).fetchone()
    else:
        g.user = User(get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone())


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(email)

        if error is None:
            key = random.randint(100000000, 1000000000)
            db.execute(
                'INSERT INTO user (username, email, password, accesslvl) VALUES (?, ?, ?, ?)',
                (email[:email.index('@')], email, generate_password_hash(password), str(-key))
            )
            db.commit()

            html = f"<html><head></head><body style=\"font-size: 20px\">\
                    <h1>Приветствуем <strong>{email[:email.index('@')]}</strong> \
                    на <a href=\"http://syllabica.com/\">сайте</a>!</h1>\
                    <p>Ваша регистрация прошла успешно</p>\
                    <p>Проверочный код — <strong>{key}</strong></p>\
                    <p>Ваш пароль — <strong>{password}</strong></p></body></html>"

            send_email("Registration", html, email)

            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()
        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('show_index'))


        flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('show_index'))

@bp.route('/accesslvl', methods = ('POST', 'GET'))
def get_accesslvl():

    res = 0 if g.user is None else g.user.config['accesslvl']

    return Response(str(res), mimetype='text/txt')

@bp.route('/edit', methods = ('POST', 'GET'))
@bp.route('/edit/<int:user_id>', methods = ('POST', 'GET'))
def edit(user_id = None):
    if not g.user :
       return render_template('auth/edit.html', user = None)

    if not g.user.is_admin or user_id is None:
        user_id = g.user.config["id"]

    db = get_db()
    if request.method == 'POST':
        sql = 'UPDATE user SET '
        if request.form['name']:
            sql += 'username = "' + request.form['name'] + '",'
        if request.form['npassword']:
            sql += 'password = "' + generate_password_hash(request.form['npassword']) + '",'
        key = random.randint(100000000,1000000000)
        if request.form['email']:
            sql += 'email = "' + request.form['email'] + '", accesslvl = "-' + str(key) + '",'

        if g.user.is_admin:
            if request.form['status']:
                sql += 'status = "' + request.form['status'] + '",'
            if request.form['accesslvl']:
                sql += 'accesslvl = "' + request.form['accesslvl'] + '",'

        if not (request.form['cpassword'] and check_password_hash(g.user.config['password'], request.form['cpassword'])):
            flash("Wrong current password")

        if g.user.is_admin or check_password_hash(g.user.config['password'], request.form['cpassword']):
            db.execute(
               sql[:-1] + ' WHERE id = ?', (user_id,)
            )
            db.commit()

            html = f"<html><head></head><body style=\"font-size: 20px\">\
                <h1>Приветствуем <strong>{request.form['name']}</strong> \
                на <a href=\"http://93.175.16.171:5000\">сайте</a>!</h1>\
                <p>Изменение Ваших данных прошло успешно</p>\
                <p>Проверочный код (при необходимости) — <strong>{key}</strong></p>\
                <p>Ваш пароль — <strong>{request.form['npassword']}</strong></p></body></html>"

            send_email("User settings", html, request.form['email'])

    user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    return render_template('auth/edit.html', user = user)

@bp.route('/list', methods = ('POST', 'GET'))
def list(user_id = None):
    if not g.user :
       return render_template('auth/edit.html', user=None)

    if not g.user.is_admin or user_id is None:
        user_id = g.user.config["id"]

    db = get_db()

    users = db.execute(
            'SELECT id, username, email, status, accesslvl FROM user'
    ).fetchall()
    return render_template('auth/list.html', users = users)

@bp.route('/check', methods=('GET', 'POST'))
def checkemail():
    if request.method == 'POST':
        code = request.form['code']
        db = get_db()
        error = None

        if g.user is None:
            error = 'You are not login.'
        elif code != str(-g.user.config['accesslvl']):
            error = 'Incorrect data.'

        if error is None:
            db.execute(
                'UPDATE user SET accesslvl = ? WHERE id = ?;',
                (1, g.user.config['id'])
            )
            db.commit()

            return redirect(url_for('show_index'))


        flash(error)
    return render_template('auth/login.html')

@bp.route('/resend', methods=('GET', 'POST'))
def resend():
    if g.user is not None:
        email = g.user.config["email"]
        key = -g.user.config["accesslvl"]
        html = f"<html><head></head><body style=\"font-size: 20px\">\
                    <h1>Приветствуем <strong>{email[:email.index('@')]}</strong> \
                    на <a href=\"http://syllabica.com/\">сайте</a>!</h1>\
                    <p>Проверочный код — <strong>{key}</strong></p>\
                    </body></html>"

        send_email("Registration", html, email)

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

