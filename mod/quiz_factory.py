import yaml, sqlite3, os


class Quiz():
    def __init__(self):
        self.form = []
        self._html = ''
        self._name = ''
        self.builder = QuizHTMLForm
        self.db = None

    def setup(self, path=None, name=None):
        if path is not None:
            self._path = path
        if name is not None:
            self._name = name

    def get_db(self):
        return sqlite3.connect(os.path.join(self._path, 'db.sqlite'), detect_types=sqlite3.PARSE_DECLTYPES)

    def load(self):
        file = open(os.path.join(self._path, 'info'), "r")
        self._name = file.read()
        file.close()
        db = self.get_db()
        classes = {
            'Str': self.builder.Str,
            'Text': self.builder.Text,
            'Choise': self.builder.Choise,
            'Select': self.builder.Select,
            'Range': self.builder.Range
        }
        # print(' >>> SELECT * FROM structure')
        for row in db.execute('SELECT * FROM structure'):
            tmp = classes[row[3]](row[5], row[4])
            tmp.title = row[1]
            tmp.name = row[2]
            self.form.append(tmp)
        for field in self.form:
            if field.__class__.__name__ in ['Choise', 'Select']:
                # print(' >>> Select * from ' + field.name)
                for val in db.execute('Select * from ' + field.name):
                    field.values[val[0]] = val[1]
        db.close()
        self.build_html()

    def get_path(self):
        return self._path

    def get_html(self):
        return self._html

    def get_name(self):
        return self._name

    def build_html(self):
        self._html = '<h1>' + self._name + '</h1>'
        self._html += ''.join(map(str, self.form))

    def build_db(self):
        file = open(os.path.join(self._path, 'info'), "w")
        file.write(self._name)
        file.close()
        db = self.get_db()
        db.row_factory = sqlite3.Row
        result_table = 'CREATE table question ( N INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER'
        # print(' >>> CREATE table structure (N INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, name TEXT, class TEXT, type TEXT, txt TEXT)')
        db.execute('CREATE table structure (N INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, name TEXT, class TEXT, type TEXT, txt TEXT)')
        for a in self.form:
            db.execute(
                'INSERT INTO structure (title, name, class, type, txt) VALUES (?, ?, ?, ?, ?)',
                (a.title, a.name, a.__class__.__name__, a.type, a.text)
            )
            # print(' >>> INSERT INTO structure (title, name, class, type, txt) VALUES (?, ?, ?, ?, ?) '+
                # ','.join(map(str,(a.title, a.name, a.__class__.__name__, a.type, a.text))))
            result_table += ', ' + a.name + ' TEXT'
            if 'values' in dir(a):
                # print(' >>> CREATE table ' + a.name + ' (N INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)')
                db.execute('CREATE table ' + a.name + ' (N INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)')
                for val in a.values:
                    # print(' >>> INSERT INTO ' + a.name + '(value) VALUES (?) ' +str(a.values[val]))
                    db.execute('INSERT INTO ' + a.name + '(value) VALUES (?)', (a.values[val],))

        # print(' >>> ' + result_table + ')')
        db.execute(result_table + ')')
        db.commit()
        db.close()


class QuizFactory(yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):

        def get_str(loader, node):
            text = loader.construct_scalar(node)
            el = cls.make_line(text, "text")
            return el

        def get_str_url(loader, node):
            text = loader.construct_scalar(node)
            el = cls.make_line(text, "url")
            return el

        def get_choise(loader, node):
            text = loader.construct_sequence(node)
            el = cls.make_choise("none", "")
            i = 0
            for a in text:
                el.values[i] = a
                i += 1
            return el

        def get_choise_add(loader, node):
            text = loader.construct_sequence(node)
            el = cls.make_choise("none", "add")
            i = 0
            for a in text:
                el.values[i] = a
                i += 1
            return el

        def get_select(loader, node):
            text = loader.construct_sequence(node)
            el = cls.make_select("none", "")
            i = 0
            for a in text:
                el.values[i] = a
                i += 1
            return el

        def get_select_add(loader, node):
            text = loader.construct_sequence(node)
            el = cls.make_select("none", "add")
            i = 0
            for a in text:
                el.values[i] = a
                i += 1
            return el

        def get_text(loader, node):
            text = loader.construct_scalar(node)
            el = cls.make_text(text, "")
            return el

        def get_range(loader, node):
            text = loader.construct_mapping(node)
            el = cls.make_range(text["words"], ','.join((text["min"], text["max"], text["step"])))
            return el

    # добавляем обработчики
        loader.add_constructor(u"!str", get_str)
        loader.add_constructor(u"!str_url", get_str_url)
        loader.add_constructor(u"!choise", get_choise)
        loader.add_constructor(u"!choise_add", get_choise_add)
        loader.add_constructor(u"!select", get_select)
        loader.add_constructor(u"!select_add", get_select_add)
        loader.add_constructor(u"!text", get_text)
        loader.add_constructor(u"!range", get_range)

        fields = loader.construct_mapping(node)
        i = 0
        b = Quiz()
        b.builder = cls
        for a in fields:
            if a == "title":
                b.setup(name=fields[a])
                continue
            fields[a].title = a
            fields[a].name = 'field' + str(i)
            i += 1
            b.form.append(fields[a])
        return b

    # ниже - без изменений

    @classmethod
    def make_line(cls, name, setup=None):
        return cls.Str(name, setup)

    @classmethod
    def make_choise(cls, name, setup=None):
        return cls.Choise(name, setup)

    @classmethod
    def make_select(cls, name, setup=None):
        return cls.Select(name, setup)

    @classmethod
    def make_text(cls, name, setup=None):
        return cls.Text(name, setup)

    @classmethod
    def make_range(cls, name, setup=None):
        return cls.Range(name, setup)

    class Str:
        pass

    class Choise:
        pass

    class Select:
        pass

    class Text:
        pass

    class Range:
        pass


class QuizHTMLForm(QuizFactory):
    yaml_tag = u'!quiz_form'

    class Str:
        def __init__(self, text, setup):
            self.text = text
            self.type = setup
            self.name = 'none'
            self.title = "none"

        def __str__(self):
            return f'<div class="quiz_section form-group"><div class="quiz_content"><span class="fiend_name">{self.title}</span><input class="form-control" name="{self.name}" type="{self.type}" value="{self.text}"/></div></div>'

        def __repr__(self):
            return "Text: " + self.title + ' as ' + self.name

    class Choise:
        def __init__(self, text, setup):
            self.text = text
            self.type = setup
            self.name = 'none'
            self.title = "none"
            self.values = {}

        def __str__(self):
            txt = f'<div class="quiz_section form-group" id="{self.name}"><div class="quiz_content"><span class="fiend_name">{self.title}</span><div class="listjssort row"><input class="form-control col-sm-11 search" class="search" placeholder="Search" /><a class="sort" data-sort="value">Sort</a></div><ul class="list radio-block"/>'
            for a in self.values:
                txt += f'<li class="quiz_selector"><input type="checkbox" name="{self.name}" value="{a}"/><span class="value">{self.values[a]}</span></li>'
            if self.type == "add":
                txt += f'<li class="quiz_selector"><span class="quiz_btn" onclick="ins_check(\'{self.name}\', this)">Добавить</span></li>'

            txt += f'</ul></div></div>'
            return txt

        def __repr__(self):
            return "Chiose: " + self.title + ' as ' + self.name + '\n' + '\n'.join(map(lambda x: str(x) + ':' + self.values[x],self.values))

    class Select:
        def __init__(self, text, setup):
            self.text = text
            self.type = setup
            self.name = 'none'
            self.title = "none"
            self.values = {}

        def __str__(self):
            txt = f'<div class="quiz_section form-group" id="{self.name}"><div class="quiz_content"><span class="fiend_name">{self.title}</span><div class="listjssort row"><input class="form-control col-sm-11 search" placeholder="Search" /><a class="sort" data-sort="value">Sort</a></div><ul class="list radio-block"/>'
            for a in self.values:
                txt += f'<li class="quiz_selector"><input type="radio" name="{self.name}" value="{a}"/><span class="value">{self.values[a]}</span></li>'
            if self.type == "add":
                txt += f'<li class="quiz_selector"><span class="quiz_btn" onclick="ins_radio(\'{self.name}\', this)">Добавить</span></li>'

            txt += f'</ul></div></div>'
            return txt

        def __repr__(self):
            return "Select: " + self.title + ' as ' + self.name + '\n' + '\n'.join(map(lambda x: str(x) + ':' + self.values[x],self.values))

    class Text:
        def __init__(self, text, setup):
            self.text = text
            self.type = setup
            self.name = 'none'
            self.title = "none"

        def __str__(self):
            return f'<div class="quiz_section form-group"><div class="quiz_content"><span class="fiend_name">{self.title}</span><textarea required class="form-control" name="{self.name}">{self.text}</textarea></div></div>'

        def __repr__(self):
            return "Text: " + self.title + ' as ' + self.name

    class Range:
        def __init__(self, text, setup):
            self.text = text
            self.type = setup
            self.name = 'none'
            self.title = "none"
            self.min, self.max, self.step = setup.split(',')
            self.bval = str((float(self.min) + float(self.max)) / 2)
            self.pre, self.post = text.split('-')

        def __str__(self):
            return f'<div class="quiz_section form-group">\
                <div class="quiz_content">\
                    <span class="fiend_name">{self.title}</span>\
                        <span class="range_text">{self.post}</span>\
                        <input name="{self.name}" type="text" class="slider" value="" data-slider-min="{self.min}" data-slider-max="{self.max}" data-slider-step="{self.step}" data-slider-value="{self.bval}"/>\
                        <span class="range_text">{self.pre}</span>\
                </div></div>'

        def __repr__(self):
            return "Range: " + self.title + ' as ' + self.name
