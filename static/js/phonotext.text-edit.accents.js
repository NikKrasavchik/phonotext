// Функции управления акцентами в четвёртом блоке страницы /edit/

function add_accent(pos, word) {
    /* 
     * отображение управления акцетом
     */
    var elem = document.getElementsByClassName('acc-' + pos)[0],
        vows = word.match(/[аоуыиэеёюя]/gi),
        cons = word.split(/[аоуыиэеёюя]/gi),
        temp = '',
        count = 0;

    for (i = 0; i < cons.length; i++) {
        if (cons[i]) {
            temp += '<span>' + cons[i] + '</span>';
            count += cons[i].length;
        }
        try {
            if (vows[i]) {
                temp += '<span class="base base-' + (pos + count) + ' var-acc acc-list" onclick="accent_choose(' + pos + ', ' + count + ', \'' + word + '\', this)">' + vows[i] + '</span>';
                count++;
            }
        } catch (e) { }
    }

    close = '<div class="btn-group accent-group"> \
                <input class="btn btn-outline-warning btn-sm" type="submit" value="<" title="Отменить добавление"> \
                <input class="btn btn-outline-primary btn-sm add-temp" disabled type="button" onclick="add_temp(,,,)" value="~" title="Добавить в текущий текст"> \
                <input class="btn btn-outline-success btn-sm add-main" disabled type="button" onclick="add_main(,,)" value="+" title="Добавить в общий словарь"> \
            </div>';
    elem.action = 'javascript:annul_add_accent(' + pos + ', \'' + word + '\')';
    elem.innerHTML = temp + close;

    color_rules(true, false);
}


function annul_add_accent(pos, word) {
    /* 
     * отмена отображения управления акцетом
     */
    var temp_num = '';

    for (o = 0; o < word.length; o++) {
        temp_num += ' base-' + (pos + o);
    }
    var elem = document.getElementsByClassName('acc-' + pos)[0],
        text = '<span class="base' + temp_num + ' acc-list">' + word + '</span>',
        input = '<input class="btn btn-outline-light btn-sm accent-del" type="submit" value="+" title="Добавить ударение">';

    elem.action = 'javascript:add_accent(' + pos + ', \'' + word + '\')';
    elem.innerHTML = text + input;

    color_rules(true, false);
}


function accent_choose(word_pos, vow_pos, word, elem) {
    /* 
     * визуализация акцента при клике
     */
    if (elem.classList.contains('main-acc')) {
        if (elem.parentElement.getElementsByClassName('add-acc').length == 0) {
            elem.classList.remove('main-acc');
            elem.classList += ' add-acc';
            elem.innerHTML = elem.innerHTML[0] + '&#768;';
            change_buttons(-1, vow_pos, word, word_pos, elem);
        } else {
            elem.classList.remove('main-acc');
            elem.innerHTML = elem.innerHTML[0];
            change_buttons(-1, -2, word, word_pos, elem);
        }
    } else if (elem.classList.contains('add-acc')) {
        elem.classList.remove('add-acc');
        elem.innerHTML = elem.innerHTML[0];
        change_buttons(-2, -1, word, word_pos, elem);
    } else {
        if (elem.parentElement.getElementsByClassName('main-acc').length == 0) {
            elem.classList += ' main-acc';
            elem.innerHTML += '&#769;';
            change_buttons(vow_pos, -2, word, word_pos, elem);
        } else {
            if (elem.parentElement.getElementsByClassName('add-acc').length == 0) {
                elem.classList += ' add-acc';
                elem.innerHTML += '&#768;';
                change_buttons(-2, vow_pos, word, word_pos, elem);
            }
        }
    }
}


function change_buttons(main_acc, add_acc, word, word_pos, elem) {
    /* 
     * изменение передаваемых атрибутов функциям add_main и add_temp, при изменении акцентов через accent_choose
     * также меняет свойство disabled соответствующих кнопок
     */
    var main = elem.parentElement.getElementsByClassName('add-main')[0],
        add = elem.parentElement.getElementsByClassName('add-temp')[0],
        old = main.attributes['onclick']['nodeValue'],
        values = old.substr(9, old.length - 10).split(',');

    if (main_acc == -2) {
        main_acc = values[1];
    }
    if (add_acc == -2) {
        if (values[2]) {
            add_acc = values[2];
        } else {
            add_acc = -1;
        }
    }

    main.attributes['onclick']['nodeValue'] = 'add_main(\'' + word + '\',' + main_acc + ',' + add_acc + ')';
    add.attributes['onclick']['nodeValue'] = 'add_temp(\'' + word + '\',' + main_acc + ',' + add_acc + ',' + word_pos + ')';
    if (main_acc >= 0) {
        main.disabled = false;
        add.disabled = false;
    } else {
        main.disabled = true;
        add.disabled = true;
    }
}


function del_custom(word, word_pos) {
    /* 
     * удаление существующего местного акцента
     */
    var cur_id = window.location.pathname.split('/');
    cur_id = cur_id[cur_id.length - 1];

    $.post('del_custom', {
        word: word,
        word_pos: word_pos,
        cur_id: cur_id
    }).done(function (response) {
        inter_analyze(true);
    }).fail(function () {
        console.log('fail');
    })
}


function add_temp(word, vow_pos, add_vow, word_pos) {
    /* 
     * добавление местного акцента
     */
    var cur_id = window.location.pathname.split('/');
    cur_id = cur_id[cur_id.length - 1];

    if (add_vow < 0) {
        add_vow = null;
    }

    $.post('change_accent', {
        word: word,
        word_pos: word_pos,
        vow_pos: vow_pos,
        add_vow: add_vow,
        cur_id: cur_id
    }).done(function (response) {
        inter_analyze(true);
    }).fail(function () {
        console.log('fail');
    })
}


function add_main(word, vow_pos, add_vow) {
    /* 
     * добавление общего акцента
     */
    if (add_vow < 0) {
        add_vow = null;
    }

    $.post('accent_add', {
        word: word,
        vow_pos: vow_pos,
        add_vow: add_vow
    }).done(function (response) {
        inter_analyze(true);
    }).fail(function () {
        console.log('fail');
    })
}
