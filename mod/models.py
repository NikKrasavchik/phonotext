# -*- coding: utf-8 -*-
'''
Модели таблиц БД
'''
import flask_sqlalchemy
from datetime import datetime

PDB = flask_sqlalchemy.SQLAlchemy()

class Analyze(PDB.Model):
    '''
    Таблица анализов
    '''
    id = PDB.Column(PDB.Integer, primary_key=True)
    base_str = PDB.Column(PDB.Text)
    base = PDB.Column(PDB.PickleType)
    syll = PDB.Column(PDB.PickleType)
    comb = PDB.Column(PDB.PickleType)
    vibr = PDB.Column(PDB.PickleType)
    repeat = PDB.Column(PDB.PickleType)
    private = PDB.Column(PDB.Boolean)
    temp = PDB.Column(PDB.Boolean)
    accents = PDB.Column(PDB.PickleType)
    custom_accents = PDB.Column(PDB.PickleType)
    timestamp = PDB.Column(PDB.DateTime, index=True, default=datetime.utcnow)
    user_id = PDB.Column(PDB.Integer)
    author = PDB.Column(PDB.Text)
    name = PDB.Column(PDB.Text)
    series = PDB.Column(PDB.Text)
    year = PDB.Column(PDB.Integer)
    settings = PDB.Column(PDB.PickleType)


class Replace(PDB.Model):
    '''
    Таблица слов для автозамены е->ё
    '''
    id = PDB.Column(PDB.Integer, primary_key=True)
    word = PDB.Column(PDB.Text)


class Accent(PDB.Model):
    '''
    Словарь ударений
    '''
    id = PDB.Column(PDB.Integer, primary_key=True)
    word = PDB.Column(PDB.Text)
    accent = PDB.Column(PDB.Integer)
    addit = PDB.Column(PDB.Integer)
