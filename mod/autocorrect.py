# -*- coding: utf-8 -*-
import re, os


def full_correct(text, log):
    '''
    Автозамена е на ё всех известных словарю слов
    '''
    file = open(os.path.join('lit','replace.txt'), 'rt', encoding='utf-8')
    dict = file.read()
    file.close()
    dict = re.split('[\\n]', dict)
    words = re.findall('[а-яa-z]*е[а-яa-z]*', text, re.I)
    replaced_words = []
    for word in words:
        start_pos = 0
        while True:
            start_pos = word.find('е', start_pos) + 1
            if start_pos == 0: break
            mark_word = word[:start_pos-1] + '?' + word[start_pos:]
            if mark_word in dict:
                mark_word = mark_word.replace('?', 'ё')
                text = text.replace(word, mark_word)
                replaced_words.append(mark_word)
                break
    return text, replaced_words



def add_correct(word):
    '''
    Добавление нового слова в словарь
    '''
    try:
        word = word.replace('ё', '?')
        file = open('replace.txt', 'at', encoding='utf-8')
        file.write(word + '\n')
        file.close()
        return 'Успешно добавлено слово: ' + word
    except:
        return 'Возникли проблемы при добавлении слова "%s"' % word



def del_correct(word):
    '''
    Удаление слова из словаря
    '''
    try:
        word = word.replace('ё', '?')
        file = open('replace.txt', 'rt', encoding='utf-8')
        lines = file.readlines()
        file.close()
        file = open('replace.txt', 'wt', encoding='utf-8')
        for line in lines:
            if line != word + '\n':
                file.write(line + '\n')
        file.close()
        return 'Успешно удалено слово: ' + word
    except:
        return 'Возникли проблемы при удалении слова "%s"' % word