class PhLetter:
    """
    @brief      Class for letter representation.
    """
    replacer = dict(zip(
        '-jйцукенгшщзхфывапролджэячсмитбю \n',
        '-jjцукенкшщскфыфапролтшэячсмитпю|/'
        ))

    repr_ch = dict(zip(
        '-jйцукенгшщзхфывапролджэячсмитбю ',
        '-jйцукэнгшщзхфывапролджэaчсмитбу '
        ))

    def __init__(self, symbol, **class_list):
        self.base_char = symbol
        symbol = symbol.lower()
        self.repr_ch = PhLetter.repr_ch.get(symbol.lower(), '')
        self.new_char = PhLetter.replacer.get(symbol.lower(), '')
        self.classes = ['chr']
        for key, value in class_list.items():
            if isinstance(value, list):
                for val in value:
                    self.classes.append(str(key) + '-' + str(val))
            else:
                self.classes.append(str(key) + '-' + str(value))

    def __str__(self):
        return self.new_char

    def __repr__(self):
        return self.base_char

    def get_html_repr(self):
        if self.base_char == "\n":
            return '<br/>'
        return '<span class="'+ ' '.join(self.classes) +'">' + self.base_char + '</span>'

    def get_repr_ch(self):
        """
        @brief      get repr char

        @param      self  The object

        @return     The repr ch.
        """
        return '<span class="'+ ' '.join(self.classes) +'">' + self.repr_ch + '</span>'

class PhText:
    '''
    Класс текстов для фонообработки
    '''
    replacer = {
        'и':{'ь': 'jи', 'ъ': 'jи'},
        'е':{' ': 'jэ', 'ь': 'jэ', 'ъ': 'jэ', 'а': 'jэ', 'о': 'jэ', 'у': 'jэ', 'ы': 'jэ',
             'и': 'jэ', 'э': 'jэ', 'е': 'jэ', 'ё': 'jэ', 'ю': 'jэ', 'я': 'jэ'},
        'ё':{' ': 'jо', 'ь': 'jо', 'ъ': 'jо', 'а': 'jо', 'о': 'jо', 'у': 'jо', 'ы': 'jо',
             'и': 'jо', 'э': 'jо', 'е': 'jо', 'ё': 'jо', 'ю': 'jо', 'я': 'jо'},
        'ю':{' ': 'jу', 'ь': 'jу', 'ъ': 'jу', 'а': 'jу', 'о': 'jу', 'у': 'jу', 'ы': 'jу',
             'и': 'jу', 'э': 'jу', 'е': 'jу', 'ё': 'jу', 'ю': 'jу', 'я': 'jу'},
        'я':{' ': 'jа', 'ь': 'jа', 'ъ': 'jа', 'а': 'jа', 'о': 'jа', 'у': 'jа', 'ы': 'jа',
             'и': 'jа', 'э': 'jа', 'е': 'jа', 'ё': 'jа', 'ю': 'jа', 'я': 'jа'},
        ' ':{' ':' '}
    }

    volwes = set('уеыаоэиюяё')

    def __init__(self, text):
        '''
        Инициализация :: первоначальная обработка текста
        '''
        perv = ' '
        perv_ch = ' '
        self.text = []
        char = 0
        word = 0
        syllable = 0

        for letter in text:
            tmp = False
            if letter in PhText.replacer:
                tmp = PhText.replacer[letter.lower()]
                if perv in tmp:
                    tmp = tmp[perv]
                else:
                    tmp = False

            if letter in set('ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'):
                char +=1
            if letter in set('ёуеыаоэяиюЁУЕЫАОЭЯИЮ'):
                syllable += 1
            if (letter in set(" \t\n\r")) and (perv not in set(' \t\n\r')):
                word += 1

            if tmp and tmp[0] == 'j':
                self.text.append(PhLetter('j',
                                          char=char,
                                          word=word,
                                          syll=[syllable, syllable+1])
                                )
                self.text[-1].base_char = ''

            if (tmp and len(tmp) == 1):
                self.text[-1].new_char = ''
            self.text.append(PhLetter(letter,
                                      char=char,
                                      word=word,
                                      syll=[syllable, syllable+1])
                            )

            tmp = self.text[-1].repr_ch
            if tmp == perv_ch:
                self.text[-1].repr_ch = ''

            if tmp != '':
                perv_ch = tmp
            perv = letter

    def __str__(self):
        return ''.join(list(map(str, self.text)))

    def __repr__(self):
        return ''.join(list(map(repr, self.text)))

    def get_repr(self)->str:
        """
        @brief      Gets text repr.

        @param      self  The object

        @return     The repr.
        """
        return '<span>' + \
               ''.join(map(lambda x: x.get_repr_ch(), self.text)) + \
               '</span>'

    def get_html_repr(self)->str:
        return '<span>' + \
               ''.join(map(lambda x: x.get_html_repr(), self.text)) + \
               '</span>'

    def get_classes(self)->set:
        """
        @brief      Gets the list of classes.

        @param      self  The object

        @return     The classes.
        """
        res = set()
        for symb in self.text:
            for cls in symb.classes:
                if cls[0:4] != 'char':
                    res.add(cls)
        return res

    def __len__(self):
        return len(self.text)

    def __getitem__(self, key):
        return self.text[key]
