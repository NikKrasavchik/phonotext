# -*- coding: utf-8 -*-
'''
Режимы поиска
'''
import re


def more_cons(syll_list: list, settings, c_pattern, v_pattern):
    '''
    Двуконсонантные (моносиллабы, группы повторяющихся согласных,
    которые не выходят за пределы одного потенциального слога)
    '''
    iter_list = []
    # выполняем проход по всем сочетаниям
    for syll in syll_list:
        count_cons = len(re.findall(c_pattern, syll[0]))
        # смотрим на все варианты сочетаний от 2-х до количества согласных
        for num_syll in range(count_cons, 1, -1):
            iterate: list = []
            while True:
                try:
                    # если можем, дополняем индексы по согласным
                    while len(iterate) != num_syll:
                        if not iterate:
                            iterate.append(re.search(c_pattern, syll[0]).start())
                        else:
                            iterate.append(re.search(c_pattern, syll[0][iterate[-1] + 1:]).start() + iterate[-1] + 1)
                    text_iter = ''
                    for i in range(len(syll[0])):
                        if i in iterate or re.match(v_pattern, syll[0][i]) is not None:
                            text_iter += syll[0][i]
                        elif re.match('[|]', syll[0][i]) is not None:
                            text_iter += '|'
                        else:
                            text_iter += '-'
                    while text_iter[0] == '-' or text_iter[0] == '|':
                        text_iter = text_iter[1:]
                    while text_iter[-1] == '-' or text_iter[-1] == '|':
                        text_iter = text_iter[:-1]
                    iter_list.append([syll[1], text_iter])
                except BaseException:
                    iterate.pop(-1)
                try:
                    while True:
                        res = (re.search(c_pattern, syll[0][iterate[-1] + 1:]))
                        if res is None:
                            iterate.pop(-1)
                        else:
                            iterate[-1] = res.start() + iterate[-1] + 1
                            break
                except BaseException:
                    break

    # создаем копию списка
    copy_list = list(iter_list)
    # убираем из списка все ложные фоносиллабемы
    if settings[0] == 'true':
        lower_l = 2
    elif settings[1] == 'true':
        lower_l = 3
    elif settings[2] == 'true':
        lower_l = 4
    if settings[2] == 'true':
        upper_l = 99
    elif settings[1] == 'true': 
        upper_l = 3
    elif settings[0] == 'true':
        upper_l = 2
    if not lower_l:
        return []
    for iterate in copy_list:
        i_len = len(set(re.findall(c_pattern, iterate[1])))
        if i_len < lower_l or i_len > upper_l:
            iter_list.remove(iterate)
    if lower_l == 2 and upper_l == 99 and settings[1] == 'false':
        for iterate in copy_list:
            if len(set(re.findall(c_pattern, iterate[1]))) == 3:
                iter_list.remove(iterate)
    return iter_list


def vibrations(iter_list: list, c_pattern, v_pattern):
    '''
    Поиск вибраций
    '''
    vibrations_list = []
    for obj in iter_list:
        if ((obj[0][0] == obj[0][-1] or
          set([obj[0][0], obj[0][1]]) == set([obj[0][-1], obj[0][-2]]) or
          len(set(re.findall(c_pattern, obj[0]))) != len(re.findall(c_pattern, obj[0]))) and
          obj[0][0] != '/' and
          len(set(re.findall(c_pattern, obj[0]))) > 1):
            vibrations_list.append([obj[1], obj[0]])
    return vibrations_list


def new_repeat(comb_list: list, c_pattern, v_pattern):
    '''
    Поиск повторов с группировкой по полному совпадению согласных
    '''
    res = []
    for i, i_value in enumerate(comb_list):
        try:
            next_val = i_value[0]
            k = i
            while next_val == i_value[0]:
                k += 1
                next_val = comb_list[k][0]
            temp = []
            temp.append(i_value)
            main_set = set(re.findall(c_pattern, i_value[1]))
            for o, o_value in enumerate(comb_list[i+1:]):
                if i_value[0] != o_value[0] and o_value[0] != next_val:
                    add_set = set(re.findall(c_pattern, o_value[1]))
                    if add_set == main_set:
                        temp.append(o_value)
            if len(temp) > 1:
                res.append(temp)
        except:
            pass
    return res