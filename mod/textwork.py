# -*- coding: utf-8 -*-
'''
Обработка текста
'''
import re
import unidecode
from app import phonotext
from app.mod import search_modes as search_modes


def text_processing(correct_text: str, settings):
    '''
    Предварительная обработка текста
    '''
    pattern = '[аоуыэюяеёи\\n]'
    vow_pos = [len(correct_text)]
    vow_pos[0:0] = [m.start() for m in re.finditer(pattern, correct_text, re.I)]
    text = correct_text.lower()
    # обозначаем перенос строки
    text = re.sub('\\n', '/', text)
    text = re.sub(r'[\s\t]{1,}', ' ', text)
    text = re.sub('[ ]', '|', text)
    text = re.sub('[^а-яa-zё|/]', '', text)
    text = re.sub('([ъь])и', r'\1йи', text)
    text = re.sub('([ ьъаоуыиэеёюя])е', r'\1йэ', text)
    # первый проход не находит двойные сочетания
    text = re.sub('(й[эоуя])е', r'\1йэ', text)
    text = re.sub('([ ьъаоуыиэеёюя])ё', r'\1йо', text)
    text = re.sub('(й[эоуя])ё', r'\1йо', text)
    text = re.sub('([ ьъаоуыиэеёюя])ю', r'\1йу', text)
    text = re.sub('(й[эоуя])ю', r'\1йу', text)
    text = re.sub('([ ьъаоуыиэеёюя])я', r'\1йа', text)
    text = re.sub('(й[эоуя])я', r'\1йа', text)
    # убираем оставшиеся мягкие и твердые знаки
    text = re.sub('[ъь]', '', text)
    # создаем общность согласных
    text = re.sub('[пб]', 'п', text)
    text = re.sub('[фв]', 'ф', text)
    text = re.sub('[тд]', 'т', text)
    text = re.sub('[сз]', 'с', text)
    text = re.sub('[йй]', 'й', text)
    if settings[0] == 'true':
        text = re.sub('[шжчщ]', 'ш', text)
    if settings[1] == 'true':
        text = re.sub('[кгх]', 'к', text)
    # убираем повторяющиеся согласные
    text = re.sub(r'([цкнгшщзхфвпрлджчсмтб])\1', r'\1', text)

    return text, vow_pos


def eng_text_processing(correct_text: str, settings):
    '''
    Предварительная обработка английского текста
    '''
    vow_pattern = 'au|ea|ee|eu|ie|oa|ou|oe|ai|i|a|o|u|\n'
    e_pattern = 'e([sd][a-z]|[abce-rt-z])'
    y_pattern = '[^ieaou](y)[^ieaou]'
    vow_pos = [len(correct_text)]
    e_pos = []
    y_pos = []
    vow_pos[0:0] = [m.start() for m in re.finditer(vow_pattern, correct_text, re.I)]
    e_pos[0:0] = [m.start() for m in re.finditer(e_pattern, correct_text, re.I)]
    y_pos[0:0] = [m.start(1) for m in re.finditer(y_pattern, correct_text, re.I)]
    print(y_pos)
    text = correct_text.lower()
    text = re.sub('\\n', '/', text)
    text = re.sub(r'[\s\t]{1,}', ' ', text)
    text = re.sub('[ ]', '|', text)
    text = re.sub('[^а-яa-zё\|/]', '', text)
    text = re.sub('b', 'p', text)                               # 0
    text = re.sub('sc(i[ieaou])|ss(i[ieaou])', r'sh\1', text)   # 0
    text = re.sub('c(i[ieaou])', r'sh\1', text)                 #+1
    text = re.sub('([a-z])ss(ur)', r'\1sh\2', text)             # 0
    text = re.sub('([a-z])[st](i[ieaou])', r'\1sh\2', text)     #+1
    # -si(on) = -su/-zu+r  = -su-/zu+V [ʃ]/ [ʒ] ?
    text = re.sub('sc([iey])', r's\1', text)                    #-1
    text = re.sub('c([iey])', r's\1', text)                     # 0
    text = re.sub('z', 's', text)                               # 0
    text = re.sub('c([aou])', r'k\1', text)                     # 0
    text = re.sub('ck', 'k', text)                              #-1
    text = re.sub('ch', 'j', text)                              #-1
    text = re.sub('g([iey])', r'j\1', text)                     # 0
    text = re.sub('([a-z])t(ure)', r'\1j\2', text)              # 0
    text = re.sub('f', 'v', text)                               # 0
    text = re.sub('wh(^o|^om|^ose|^ole)', r'v\1', text)         #-1
    text = re.sub('w', 'v', text)                               # 0
    text = re.sub('ph', 'v', text)                              #-1
    text = re.sub('(au|ou)gh', r'\1v', text)    # ?             #-1
    text = re.sub('g([aou])', r'k\1', text)                     # 0
    text = re.sub('c([aou])', r'k\1', text)                     # 0
    text = re.sub('x', 'ks', text)                              #+1
    text = re.sub('t', 'd', text)                               # 0
    text = re.sub('ll', 'l', text)                              #-1
    text = re.sub('mm', 'm', text)                              #-1
    text = re.sub('nn', 'n', text)                              #-1
    text = re.sub('rr', 'r', text)                              #-1
    text = re.sub('([^ieaou])y([^ieaou])', r'\1ai\2', text)
    text = re.sub('([^e])e([sd][^a-z]|[^a-z])', r'\1\2', text)  #-1
    text = re.sub('([gtckprwdv])h', r'\1', text)                #-1
    #th- = s ?
    #oo  = u ?
    #kn- = n ?
    #-ng = n ?
    #[...]
    #закрытый/открытый слог ?

    return text, vow_pos, e_pos, y_pos



def separation(text: str, vowels: list, *dift_pos):
    '''
    Разделение текста
    '''
    if not dift_pos:
        pattern = '[аоуыэюяеёи/]'
        vow_pos = [-1, len(text)]
        vow_pos[1:1] = [m.start() for m in re.finditer(pattern, text)]
        syll_list = []
        i = 0
        while i < len(vow_pos) - 2:
            sep = text[vow_pos[i]+1:vow_pos[i+2]]
            if ' ' not in sep:
                if '/' not in sep:
                    syll_list.append([sep, vowels[i]])
                else:
                    syll_list.append(['/', vowels[i]])
            i += 1
    else:
        print(text)
        vowels.extend(dift_pos[0])
        vowels.extend(dift_pos[1])
        print(vowels)
        vowels = list(set(vowels))
        vowels.sort()
        print(vowels)
        pattern = 'au|ea|ee|eu|ie|oa|ou|oe|ai|i|a|o|u|/'
        e_pattern = 'e[sd][a-z]|e[abce-rt-z]'
        vow_pos = [-1, len(text)]
        vow_pos[1:1] = [m.start() for m in re.finditer(pattern, text)]
        vow_pos[1:1] = [m.start() for m in re.finditer(e_pattern, text)]
        vow_pos = list(set(vow_pos))
        vow_pos.sort()
        syll_list = []
        i = 0
        while i < len(vow_pos) - 2:
            if re.search('au|ea|ee|eu|ie|oa|ou|oe|ai', text[vow_pos[i]:vow_pos[i]+2]) is None:
                sep = text[vow_pos[i]+1:vow_pos[i+2]]
            else:
                sep = text[vow_pos[i]+2:vow_pos[i+2]]
            if ' ' not in sep:
                if '/' not in sep:
                    syll_list.append([sep, vowels[i]])
                else:
                    syll_list.append(['/', vowels[i]])
            i += 1
    print(syll_list)
    return syll_list


def go_analyze(base_text: str, settings, lang, custom_accents = {}):
    '''
    Обработка текста
    '''
    if lang == 'russian':
        c_pattern = '[бвгджзйклмнпрстфхцчшщ]'
        v_pattern = '[аоуыиэюяёе]'
    else:
        c_pattern = '[bcdfghklmnpqrstvxyz]'
        v_pattern = '[aioeu]'
    if lang == 'russian':
        correct_text, replaced_words = full_correct(base_text)
        accent_words = get_accent(correct_text, custom_accents)
        new_text, vow_pos = text_processing(correct_text, settings[1])
        line_list: list = []
        syll_list = separation(new_text, vow_pos)
        comb_list = search_modes.more_cons(syll_list, settings[0], c_pattern, v_pattern)
        new_repeat = search_modes.new_repeat(comb_list, c_pattern, v_pattern)
        vibrations = search_modes.vibrations(syll_list, c_pattern, v_pattern)
        line_list[0:0] = [m for m in re.split('[\r\n]', correct_text)]
        for l_ind, line in enumerate(list(line_list)):
            copy = list(line)
            line_list[l_ind] = []
            for symb in copy:
                match = re.match(v_pattern, symb, re.I)
                if match:
                    line_list[l_ind].append([symb, 1])
                else:
                    line_list[l_ind].append([symb, 0])
    else:
        accent_words = get_accent(base_text, custom_accents)
        new_text, vow_pos, e_pos, y_pos = eng_text_processing(base_text, settings[1])
        line_list: list = []
        syll_list = separation(new_text, vow_pos, e_pos, y_pos)
        comb_list = search_modes.more_cons(syll_list, settings[0], c_pattern, v_pattern)
        new_repeat = search_modes.new_repeat(comb_list, c_pattern, v_pattern)
        vibrations = search_modes.vibrations(syll_list, c_pattern, v_pattern)
        line_list[0:0] = [m for m in re.split('[\r\n]', base_text)]
        for l_ind, line in enumerate(list(line_list)):
            copy = list(line)
            line_list[l_ind] = []
            temp = ''
            for symb in copy:
                if len(temp) < 3:
                    temp += symb
                    if len(temp) == 3:
                        if re.match('au|ea|ee|eu|ie|oa|ou|oe|ai', temp[:2], re.I):
                            line_list[l_ind].append([temp[:2], 1])
                            temp = temp[2]
                        elif re.match('([^ieaou])y([^ieaou])', temp, re.I):
                            line_list[l_ind].append([temp[0], 0])
                            line_list[l_ind].append(['y', 1])
                            temp = temp[2]
                        elif re.match('e[sd][^a-z]', temp, re.I) or re.match('e[^a-z]', temp[:2], re.I):
                            line_list[l_ind].append([temp[0], 0])
                            line_list[l_ind].append([temp[1], 0])
                            temp = temp[2]
                        else:
                            if re.match(v_pattern, temp[0], re.I):
                                line_list[l_ind].append([temp[0], 1])
                            else:
                                line_list[l_ind].append([temp[0], 0])
                            temp = temp[1:]
            if len(temp) == 2:
                if re.match('au|ea|ee|eu|ie|oa|ou|oe|ai', temp, re.I):
                    line_list[l_ind].append([temp, 1])
                elif re.match('e[^a-z]', temp, re.I):
                    line_list[l_ind].append([temp[:1], 0])
                elif re.match('[^ieaou]y', temp, re.I):
                    line_list[l_ind].append([temp[0], 0])
                    line_list[l_ind].append(['y', 1])
                else:
                    if re.match(v_pattern, temp[0], re.I):
                        line_list[l_ind].append([temp[0], 1])
                    else:
                        line_list[l_ind].append([temp[0], 0])
                    if re.match(v_pattern, temp[1], re.I):
                        if temp[1] == 'e':
                            line_list[l_ind].append([temp[1], 0])
                        else:
                            line_list[l_ind].append([temp[1], 1])
                    else:
                        line_list[l_ind].append([temp[1], 0])
            if len(temp) == 1 and temp != 'e':
                if re.match('y', temp, re.I):
                    line_list[l_ind].append([temp, 1])
                elif re.match(v_pattern, temp, re.I):
                    line_list[l_ind].append([temp, 1])
                else:
                    line_list[l_ind].append([temp, 0])

    analyze = {
        'syll': syll_list,
        'comb': comb_list,
        'vibr': vibrations,
        'rep': new_repeat,
        'lines': line_list,
        'replaced': [],
        'accents': accent_words,
        'base': base_text,
        'custom': custom_accents,
        'settings': settings,
        'lang': lang
    }
    return analyze


def full_correct(text: str):
    '''
    Замена е->ё
    '''
    diction = app.phonotext.dict_get()
    text += ' temp'
    text = text[0:1] + text[1:]
    words = re.findall(r'([а-яёa-z-]*е[а-яёa-z-]*)[^а-яёa-z-]*', text, re.I)
    indexes = [(m.start(1), m.end(1)) for m in re.finditer(r'([а-яёa-z-]*е[а-яёa-z-]*)[^а-яёa-z-]*', text, re.I)]
    replaced_words = []
    for i, word in enumerate(words):
        temp_word = word
        start_pos = 0
        while True:
            start_pos = temp_word.find('е', start_pos) + 1
            if start_pos == 0:
                break
            mark_word = temp_word[:start_pos-1] + '?' + temp_word[start_pos:]
            if mark_word.lower() in diction:
                mark_word = mark_word.replace('?', 'ё')
                text = text[:indexes[i][0]] + mark_word + text[indexes[i][1]:]
                replaced_words.append(mark_word)
                break
    text = text[:len(text) - 5]
    return text, replaced_words


def get_accent(text: str, custom):
    '''
    Определение ударений по словарю
    '''
    diction = app.phonotext.accent_get()
    words = re.findall(r'[а-яёa-z-]*', text, re.I)
    indexes = [(m.start(0), m.end(0)) for m in re.finditer(r'[а-яёa-z-]*', text, re.I)]
    word_accents = [[], [], []]
    # проходим по всем словам
    for i, word in enumerate(words):
        cus = False
        if word != '':
            accents = []
            if word in custom:
                for var in custom[word]:
                    if int(var[0]) == indexes[i][0]:
                        word_accents[0].append([word, indexes[i][0], [var[1], var[2]]])
                        word_accents[1].append(indexes[i][0] + int(var[1]))
                        if var[2]:
                            word_accents[2].append(indexes[i][0] + int(var[2]))
                        cus = True
                        break
            if cus == False:
                vows = [(m.start(0), m.end(0)) for m in re.finditer(r'[аоуыиэеёюя]', word)]
                # смотрим на все одиночные ударения
                for vow in vows:
                    if [word.lower(), vow[0], None] in diction:
                        result = [word, vow[0], indexes[i][0], None]
                        accents.append(result)
                # смотрим на все двойные ударения
                for main_vow in vows:
                    for add_vow in vows:
                        if [word.lower(), main_vow[0], add_vow[0]] in diction:
                            result = [word, main_vow[0], indexes[i][0], add_vow[0]]
                            accents.append(result)
                # если нет совпадений записываем только в первый массив
                if len(accents) is None:
                    word_accents[0].append([word, indexes[i][0], None])
                # если совпадение только одно, записываем в первый массив, и единственный индекс в финальный список
                elif len(accents) == 1:
                    word_accents[0].append([word, indexes[i][0], [accents[0][1], accents[0][3]]])
                    word_accents[1].append(indexes[i][0] + accents[0][1])
                    if accents[0][3]:
                        word_accents[2].append(indexes[i][0] + accents[0][3])
                # если совпадений больше, записываем их еще одним массивом всех вариантов в первый массив
                else:
                    result = []
                    for var in accents:
                        result.append([var[1], var[3]])
                    word_accents[0].append([word, indexes[i][0], result])
    return word_accents
