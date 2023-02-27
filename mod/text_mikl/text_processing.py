''' module for working with phonotext by the chain of responsibility '''

from math import log
from collections import defaultdict
import abc
import yaml
import re
from app.mod.accents import get_accents

ZERO_SPACE = u'\u200B'


def finder_volv(data):
    '''
    find volv generator
    '''
    curr = 0
    last = len(data)
    while curr < last:
        if data[curr].is_volve:
            yield curr
        curr += 1
    yield curr


def finder_cons(data):
    '''
    find cons generator
    '''
    curr = 0
    last = len(data)
    while curr < last:
        if data[curr].is_consonant:
            yield curr
        curr += 1
    yield curr


def get_filter_com_rus(min_pwr, max_pwr):

    def rus_filter_comb(indexes, vol_pos, txt, positions):

        if len(set(txt[-3:])) < 3:
            return False, 0
        if indexes[0] == vol_pos[0]:
            pwr = 2
        elif indexes[2] == vol_pos[0]:
            pwr = 1
        else:
            pwr = 3
        pwr += 5 if indexes[2] - indexes[0] - txt.count('|') == 2 else 0
        pwr += 0 if txt.find('|') != -1 else 2
        pwr += 0 if txt.find('й', -3) != -1 else 4
        pwr += 1 if positions.find(b'\x01', -3) != -1 else 0
        pwr /= 15
        return min_pwr <= pwr <= max_pwr, pwr

    return rus_filter_comb


def load_config(filename):
    '''
    load yaml file from filename
    '''
    with open(filename, 'r', encoding="utf-8") as stream:
        try:
            config = yaml.load(stream, Loader=yaml.SafeLoader)

            return [
                ModifyEvent(config['modifications']),
                JoinEvent(config['as_one']),
                NumberEvent(config['volves'], config['consonants']),
                SameEvent(list(config['alphabet']) + config['as_same']),
                SPmaxEvent(),
                CombinationsEvent(2, get_filter_com_rus(0, 11)),
                RepeatEvent(),
                RepeatRecountEvent(),
            ]
            # return config
        except yaml.YAMLError as exc:
            print(f'ERROR {exc}')

        return None


class AbstractEvent(abc.ABC):
    '''
    Abstract event ca
    '''
    @abc.abstractmethod
    def __init__(self):
        pass


class Letter():
    ''' class for letter '''

    def __init__(self, char, vchar = None):
        self.origin = char if vchar is None else vchar
        self.technic = char
        self.printable = char
        self.is_consonant = False
        self.is_volve = False
        self.syll = 0
        self.pwr = 0
        self.number = 0
        self.word = 0
        self.p_end = 0
        self.accent = False

    def __str__(self):
        return self.origin + '(' + "".join([self.technic, self.printable]) + ')'

    def __repr__(self):

        return "'".join([
            self.origin,
            self.technic,
            self.printable,
            'C' if self.is_consonant else '-',
            'V' if self.is_volve else '-',
            str(self.syll),
            str(self.number),
            str(self.word)
        ])


class Phonotext():
    ''' phonotext is a a list of Letters '''

    def __init__(self, text, visual_text = None):
        if visual_text is None:
            self.basetext = [Letter(x) for x in text.lower()]
        else:
            self.basetext = [Letter(x, y) for x, y in zip(text.lower(), visual_text)]

        self.repeats = {}

    def count_letters(self):
        count_symbols = count_volves = 0
        for symb in self.basetext:
            if symb.is_consonant:
                count_symbols += 1
            if symb.is_volve and symb.printable not in ["--endl",'\n']:
                count_volves += 1
                count_symbols += 1
        return count_volves, count_symbols

    def get_origin(self):
        return ''.join([x.origin for x in self.basetext])

    def get_technic(self):
        return ''.join([x.technic for x in self.basetext])

    def get_printable(self):
        return ''.join([x.printable for x in self.basetext])

    def __repr__(self):
        return ''.join([repr(x) for x in self.basetext])

    def __len__(self):
        return len(self.basetext)


class TextProcessorHandler():
    def __init__(self, succesor=None):
        self.__succesor = succesor

    def handle(self, obj, conf):
        if self.__succesor is not None:
            return self.__succesor.handle(obj, conf)


class SameEvent(AbstractEvent):
    def __init__(self, rules):
        self.rules = dict()
        for r in rules:
            for ch in r:
                self.rules[ch] = r[0]


class SameProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, SameEvent):
            for i in range(len(obj.basetext)):
                obj.basetext[i].technic = conf.rules.get(obj.basetext[i].printable, ZERO_SPACE)
                if obj.basetext[i].technic in {ZERO_SPACE, '|'}:
                    obj.basetext[i].printable = obj.basetext[i].technic
        else:
            super().handle(obj, conf)


class NumberEvent(AbstractEvent):
    def __init__(self, volves, consonants):
        self.volves = set(volves)
        self.consonants = set(consonants)
        self.words = self.volves.union(self.consonants)


class NumberProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, NumberEvent):
            i = 0
            j = 1
            k = 1
            num = 1
            space = False
            # print(conf.volves, conf.consonants)

            for l_number in range(len(obj.basetext)):
                letter = obj.basetext[l_number]
                letter.number = i
                letter.word = k
                letter.w_pos = [num, 0]
                # print(' ', letter.technic, letter.printable, sep='', end='')
                if letter.technic in " |\n":
                    if not space:
                        k += 1
                        if num < 3:
                            while num > 1:
                                num -= 1
                                obj.basetext[l_number - num].w_pos = [0, 0]
                                num -= 1
                        while num > 1:
                            num -= 1
                            obj.basetext[l_number - num].w_pos[1] = -num
                            num -= 1

                    space = True
                else:
                    space = space and letter.technic not in conf.words
                if letter.technic == "\n":
                    stopper = obj.basetext[l_number - 1].syll - 3
                    tmp = 1
                    while obj.basetext[l_number - tmp].syll > stopper and obj.basetext[l_number - tmp].technic != "\n":
                        obj.basetext[l_number - tmp].p_end = 1
                        tmp += 1
                if letter.printable in conf.volves:
                    # print(0, end='')
                    letter.is_volve = True
                    j += 1
                if letter.printable in conf.consonants:
                    # print(1, end='')
                    letter.is_consonant = True
                letter.syll = j
                i += 1
                num += 1
            # print()
        else:
            super().handle(obj, conf)


class JoinEvent(AbstractEvent):
    def __init__(self, rules):
        self.rules = defaultdict(dict)
        for a in rules:
            self.rules[a[0]] = a


class JoinProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, JoinEvent):
            i = 1
            while i < len(obj.basetext):
                tmp_a = obj.basetext[i - 1].origin
                tmp_b = obj.basetext[i].origin
                if tmp_a in conf.rules:
                    if tmp_a + tmp_b == conf.rules[tmp_a]:
                        obj.basetext[i - 1].origin = tmp_a + tmp_b
                        obj.basetext[i - 1].printable = tmp_a + tmp_b
                        obj.basetext[i - 1].technic = tmp_a + tmp_b
                        obj.basetext.pop(i)
                        i -= 1
                    if tmp_b == "\U00000301": #accent
                        obj.basetext[i - 1].printable = tmp_a + tmp_b
                        obj.basetext[i - 1].accent = True
                        obj.basetext.pop(i)

                i += 1
        else:
            super().handle(obj, conf)


class ModifyEvent(AbstractEvent):
    def __init__(self, rules):
        self.rules = defaultdict(dict)
        for a in rules:
            self.rules[a[0]][a[1]] = rules[a]


class ModifyProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, ModifyEvent):
            i = 1
            while i < len(obj.basetext):
                tmp_a = obj.basetext[i - 1].origin
                tmp_b = obj.basetext[i].origin
                if tmp_a in conf.rules:
                    if tmp_b in conf.rules[tmp_a]:
                        tmp_c = conf.rules[tmp_a][tmp_b]
                        obj.basetext.insert(i, Letter(ZERO_SPACE))
                        obj.basetext[i - 1].printable = tmp_c[0]
                        obj.basetext[i + 0].printable = tmp_c[1]
                        obj.basetext[i + 1].printable = tmp_c[2]
                i += 1
        else:
            super().handle(obj, conf)


class SPmaxEvent(AbstractEvent):
    def __init__(self):
        pass


class SPmaxProcessor(TextProcessorHandler):
    def handle(self, obj, conf):
        if isinstance(conf, SPmaxEvent):
            iterator = finder_volv(obj.basetext)
            obj.SP = list()
            start = 0
            middle = next(iterator)
            i = 0
            for end in iterator:
                obj.SP.append(Phonotext(''))
                obj.SP[-1].basetext = obj.basetext[start:end]
                i += 1
                start = middle + 1
                middle = end
                if end < len(obj.basetext) and obj.basetext[end].origin == "\n":
                    start = middle + 1
                    middle = next(iterator)
                if obj.SP[-1].count_letters()[1] == 0:
                    obj.SP.pop()

        else:
            super().handle(obj, conf)


class CombinationsEvent(AbstractEvent):
    def __init__(self, max_cons, filter_combination):
        self.max_cons = max_cons
        self.filter_combination = filter_combination


class CombinationsProcessor(TextProcessorHandler):

    def combinations(self, s, N, filter_combination):
        N += 1
        pos_vol = list(finder_volv(s))[:-1]
        pos_cons = list(finder_cons(s))[:-1]
        n = len(pos_cons)
        poses = {i: [i] for i in range(n)}
        indexes = []
        # for i in range(n-1):
        #     if i not in poses:
        #         continue
        #     for j in range(i+1, n):
        #         if s[pos_cons[i]].technic == s[pos_cons[j]].technic:
        #             poses[i].append(j)
        #             poses.pop(j)

        tmp_cons = list(poses.keys())
        cons_num = 2 ** len(tmp_cons)
        for i in range(cons_num):
            tmp = bin(cons_num + i)[2:]
            if tmp.count('1') == N:
                indexes.append([])
                for j in range(1, len(tmp)):
                    if tmp[j] == '1':
                        indexes[-1].append(tmp_cons[j - 1])
        res = []
        for tmp in indexes:
            tmp = [pos_cons[j] for x in tmp for j in poses[x]] + pos_vol
            tmp.sort()
            if len({s[i].technic for i in tmp}) < N:
                continue
            lst = ''.join([s[i].technic for i in range(tmp[0], tmp[-1] + 1)])
            lst += '-' + ''.join([s[i].printable for i in tmp])
            positions = b''.join([s[i].w_pos[0].to_bytes(1, "little") for i in tmp])
            flt = filter_combination(tmp, pos_vol, lst, positions)
            if flt[0]:
                # for i in tmp:
                #     s[i].pwr += flt[1] / N
                res.append([[s[i] for i in tmp], flt[1]])
        return res

    def handle(self, obj, conf):
        if isinstance(conf, CombinationsEvent):
            obj.combs = list()
            for syllab in obj.SP:
                obj.combs.append(self.combinations(syllab.basetext, conf.max_cons, conf.filter_combination))
        else:
            super().handle(obj, conf)


def list_update(a, b):
    if b[1] > a[1]:
        a[1] = b[1]

    for el in b[0]:
        if a[0][0].number > el.number:
            a[0].insert(0, el)
            continue
        for i in range(len(a[0]) - 1):
            if a[0][i].number < el.number < a[0][i + 1].number:
                a[0].insert(i + 1, el)
        if a[0][-1].number < el.number:
            a[0].append(el)

class RepeatEvent(AbstractEvent):
    def __init__(self):
        pass


class RepeatProcessor(TextProcessorHandler):
    class Repeat:
        def __init__(self):
            self.count = 0
            self.power = 0
            self.letters = defaultdict(int)
            self.combs = []
            self._words = None

    def handle(self, obj, conf):
        if isinstance(conf, RepeatEvent):
            obj.repeats = defaultdict(RepeatProcessor.Repeat)
            for n_syll in range(len(obj.combs)):
                for comb in obj.combs[n_syll]:
                    a = [[], defaultdict(int)]
                    for i in comb[0]:
                        if i.is_consonant:
                            a[0].append(i.technic)
                        a[1][i.number] = n_syll
                    tmp = frozenset(a[0])
                    obj.repeats[tmp]._words = tmp
                    obj.repeats[tmp].count += 1
                    obj.repeats[tmp].power += comb[1]
                    obj.repeats[tmp].letters.update(a[1])
                    if len(obj.repeats[tmp].combs) > 0 and obj.repeats[tmp].combs[-1][0][-1].number >= comb[0][0].number:
                        list_update(obj.repeats[tmp].combs[-1], comb)
                    else:
                        obj.repeats[tmp].combs.append(comb)

        else:
            super().handle(obj, conf)


class RepeatRecountEvent(AbstractEvent):
    def __init__(self):
        pass


class RepeatRecountProcessor(TextProcessorHandler):
    @staticmethod
    def get_pwr(a, b):
        if a.technic != b.technic:
            return 0

        dist = b.syll - a.syll
        if dist < 1:
            return 0

        pwr = 0
        mul = 1
        dist_w = b.word - a.word

        pwr = 1 / dist + 1 / (dist_w + 2)
        if a.origin == b.origin and a.is_consonant:
            mul += 1
        mul *= 1 / (1 + a.w_pos[0] + b.w_pos[0])
        # if a.w_pos[0] == b.w_pos[0] and a.w_pos[0] != 0:
        #     mul += 1
        # if a.w_pos[1] == b.w_pos[1] and a.w_pos[1] != 0:
        #     mul += 0
        return pwr * mul  # * 2 / max(1, b.w_pos[0] - b.w_pos[1] + a.w_pos[0] - a.w_pos[1])

    @staticmethod
    def get_pwr_combs(a, b):
        pwr = 0
        for i in range(len(a[0])):
            for j in range(len(b[0])):
                pwr += RepeatRecountProcessor.get_pwr(a[0][i], b[0][j])

        mul_1 = 1
        mul_2 = 1
        for i in range(len(a[0]) - 1):
            mul_1 *= a[0][i + 1].number - a[0][i].number
        for i in range(len(b[0]) - 1):
            mul_2 *= b[0][i + 1].number - b[0][i].number

        mul = 10 * a[1] * b[1] * (1 + a[0][-1].p_end + b[0][-1].p_end)

        # dist = (a[0][0].number + a[0][1].number + a[0][2].number) // 3 - (b[0][0].number + b[0][1].number + b[0][2].number) // 3

        pwr *= 1 / (mul_1 + 1) + 1 / (mul_2 + 1)

        # if dist < 3:
        #     pwr *= 0.001
        # else:
        #     pwr *= 1/dist

        return pwr * mul

    def handle(self, obj, conf):
        if isinstance(conf, RepeatRecountEvent):
            for x in obj.repeats:
                obj.repeats[x].power = obj.repeats[x].power, obj.repeats[x].power / obj.repeats[x].count
                obj.repeats[x].count = 1
                last = None
                # for y in obj.repeats[x].letters:
                for y in obj.repeats[x].combs:
                    if last is None:
                        last = y
                        continue
                    # if obj.basetext[y].syll - obj.basetext[last].syll > 1:
                    if y[0][0].number - last[0][-1].number > 0:
                        obj.repeats[x].count += 1

            for rep in obj.repeats.values():
                pwr = 0
                # tmp = list(rep.letters.keys())
                # for i in range(len(tmp)-1):
                #     for j in range(1,len(tmp)):
                #         pwr += self.get_pwr(obj.basetext[tmp[i]], obj.basetext[tmp[j]])
                # rep.power = pwr, rep.power[1]

                for i in range(len(rep.combs) - 1):
                    for j in range(i, len(rep.combs)):
                        tmp = self.get_pwr_combs(rep.combs[i], rep.combs[j])
                        pwr += tmp
                rep.power = pwr, rep.power[1]
        else:
            super().handle(obj, conf)


CONFIG = {
    'rus' : load_config("./app/mod/text_mikl/russian.yaml"),
    'eng' : load_config("./app/mod/text_mikl/english.yaml"),
    'latin' : load_config("./app/mod/text_mikl/latin.yaml")
}

PROCESSOR = TextProcessorHandler()
PROCESSOR = ModifyProcessor(PROCESSOR)
PROCESSOR = SameProcessor(PROCESSOR)
PROCESSOR = JoinProcessor(PROCESSOR)
PROCESSOR = SPmaxProcessor(PROCESSOR)
PROCESSOR = CombinationsProcessor(PROCESSOR)
PROCESSOR = NumberProcessor(PROCESSOR)
PROCESSOR = RepeatProcessor(PROCESSOR)
PROCESSOR = RepeatRecountProcessor(PROCESSOR)
