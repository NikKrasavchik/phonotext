// Функции главной страницы

function index_start(lang) {
    /* 
     * добавление анализа
     */
    var text = document.getElementById('main_text').value;
    text = text.replace(/^[\s]*/g, '').replace(/[\s]*$/g, '').replace(/[\u0301\u0300]/g, '');
    $.post('interact/', {
        text: text,
        lang: lang
    }).done(function (response) {
        window.location.href = window.location.pathname.replace('/index', '/edit/') + jQuery.parseJSON(response);
    }).fail(function () {
        console.log('fail')
    })
}


function paginate(field, req, search) {
    /* 
     * запрос результатов пагинации на главной странице
     */
    $.post('paginate', {
        field: field,
        req: req,
        search: search
    }).done(function (response) {
        paginate_append(response, field);
    }).fail(function () {
        console.log('fail')
    });
}


function paginate_append(response, field) {
    /* 
     * отображение результатов пагинации для (личной истории анализов / чужой истории анализов / результатов поиска)
     */
    var addit = jQuery.parseJSON(response),
        parsed = jQuery.parseJSON(addit[0]),
        month = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'],
        fields = {
            all: 'all_hist',
            my: 'my_hist',
            search: 'search_hist'
        },
        myNode = document.getElementById(fields[field]);

    try {
        while (myNode.firstChild) {
            myNode.removeChild(myNode.firstChild);
        }
    } catch (e) { }

    if (parsed[0]) {
        if (field == 'search' && (addit[3] || addit[2])) {
            str =  '<form id="' + field + '_prev" action="javascript:paginate(\'' + field + '\', ' + addit[3] + ', \'' + addit[4] + '\')"></form>\
                    <form id = "' + field + '_next" action = "javascript:paginate(\'' + field + '\', ' + addit[2] + ', \'' + addit[4] + '\')"></form>\
                    <div class="col-1 text-center">\
                        <button type = "submit" class="btn btn-secondary" form = "' + field + '_prev"' + (addit[3] ? '' : ' disabled') + ' ><</button>\
                    </div>'
            document.getElementById(fields[field]).innerHTML += str;
        }

        for (i = 0; i < parsed.length; i++) {
            var str = '',
                max = 1;

            str += '<div class="card text-center history-card"><div class="card-body">';
            for (o = 0; o < parsed[i]['base'].length; o++) {
                if (max > 4) {
                    break;
                }
                for (k = 0; k < parsed[i]['base'][o].length; k++) {
                    str += '<span>' + parsed[i]['base'][o][k][0] + '</span>';
                }
                str += '<br />';
                max++;
            }

            str += '</div><div class="card-footer text-muted history"><table class="table-sm table-borderless"><tr><td><small>Автор: ';
            for (o = 0; o < addit[1].length; o++) {
                if (addit[1][o][1] == parsed[i]['user_id']) {
                    str += addit[1][o][0];
                    break;
                }
            }

            str += '</small></td><td rowspan="2"><a href="text/';
            str += parsed[i]['id'];
            str += '" class="btn-sm btn-outline-info cont-read">Читать далее</a></td></tr><tr><td><small>Дата: ';
            date = new Date(parsed[i]['timestamp']);
            str += (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':' + (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) +
                ' | ' + (date.getDate() < 10 ? '0' + date.getDate() : date.getDate()) + ' ' + month[date.getMonth()] + ' ' + date.getFullYear();
            str += '</small></td></tr></table></div></div>'

            var div = document.createElement('div');
            div.classList.add("col-2.5")
            div.classList.add("text-center")
            div.innerHTML = str;
            document.getElementById(fields[field]).appendChild(div);
        }

        div = document.createElement('div');
        str = '';
        if (addit[3] || addit[2]) {
            if (field == 'search') {
                str = '<button type="submit" class="btn btn-secondary" form="' + field + '_next"' + (addit[2] ? '' : ' disabled') + '>></button>'
                div.classList.add("col-1")
                div.classList.add("text-center")
            } else {
                str =  '<form id="' + field + '_prev" action="javascript:paginate(\'' + field + '\', ' + addit[3] + ')"></form>\
                        <form id = "' + field + '_next" action = "javascript:paginate(\'' + field + '\', ' + addit[2] + ')"></form>\
                        <div class="btn-group" role="group">\
                            <button type = "submit" class="btn btn-secondary" form = "' + field + '_prev"' + (addit[3] ? '' : ' disabled') + ' ><</button>\
                            <button type="submit" class="btn btn-secondary" form="' + field + '_next"' + (addit[2] ? '' : ' disabled') + '>></button>\
                        </div>'
            }
        }

        div.innerHTML = str;
        document.getElementById(fields[field]).appendChild(div);
    } else {
        if (field == 'search') {
            document.getElementById('search_section').style.display = 'none';
        } else if (field == 'all') {
            document.getElementById('all_hist').innerHTML = '<div class="alert alert-secondary" role="alert">Открытые анализы других пользователей пока что отсутствуют</div>';
            document.getElementById('all_title').style.display = 'none';
        } else if (field == 'my') {
            document.getElementById('my_hist').innerHTML = '<div class="alert alert-secondary" role="alert">Вы ещё не делали анализы</div>';
            document.getElementById('my_title').style.display = 'none';
        }
    }
}


function search() {
    /* 
     * запрос результатов поиска
     */
    var res = document.getElementById('search_input').value;
    $.post('search', {
        search: res
    }).done(function (response) {
        document.getElementById('search_section').style.display = 'block';
        paginate_append(response, 'search');
    }).fail(function () {
        console.log('fail')
    })
}


// Функции словарей

function dict_red(mark, word = 0) {
    /* 
     * изменение словаря автозамены "е->ё" через строку "словарь автозамены"
     * также вызывается с маркером "del" кнопкой рядом со словом в правом списке /dict_edit
     * используется на /dict_edit и /index
     */
    if (word == 0) {
        word = document.getElementById('autoreplace_input').value;
    }

    $.post('dict_red', {
        word: word,
        mark: mark
    }).done(function (response) {
        var str = '<div class="alert alert-primary alert-dismissible fade show" role="alert" align="center">' + (jQuery.parseJSON(response)[2]) +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>';
        document.getElementById('message_block').innerHTML = str;

        if (window.location.pathname == '/base/dict_edit') {
            dict_trigger('rep');
        }
    }).fail(function () {
        console.log('fail')
    })
}


function accent_red(mark, word = 0) {
    /* 
     * изменение словаря ударений через строку "словарь ударений"
     * также вызывается с маркером "del" кнопкой рядом со словом в левом списке /dict_edit
     * используется на /dict_edit и /index
     */
    if (word == 0) {
        word = document.getElementById('accent_input').value;
    }

    $.post('accent_red', {
        word: word,
        mark: mark
    }).done(function (response) {
        var str = '<div class="alert alert-primary alert-dismissible fade show" role="alert" align="center">' + (jQuery.parseJSON(response)[2]) +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>';
        document.getElementById('message_block').innerHTML = str;

        if (window.location.pathname == '/base/dict_edit') {
            dict_trigger('acc');
        }
    }).fail(function () {
        console.log('fail')
    })
}


// Функции страницы словарей

function dict_trigger(mark) {
    /* 
     * обновление отображения словарей автозамены и ударений
     */
    $.post('dict_reload', {
        mark: mark
    }).done(function (response) {
        var res = jQuery.parseJSON(response),
            temp = '';
        if (mark == 'acc') {
            for (i = 0; i < res.length; i++) {
                if (res[i][2] || res[i][2] == 0) {
                    if (res[i][2] > res[i][1]) {
                        temp += '<form method=post action="javascript:accent_red(\'del\', \'' +
                            res[i][0].substr(0, res[i][1]) + '1' + res[i][0].substr(res[i][1], res[i][2] - res[i][1]) + '2' + res[i][0].substr(res[i][2]) + '\')"><span>' +
                            res[i][0].substr(0, res[i][1] + 1) + '&#769;' + res[i][0].substr(res[i][1] + 1, res[i][2] - res[i][1]) + '&#768;' + res[i][0].substr(res[i][2] + 1) + '</span>';
                    } else {
                        temp += '<form method=post action="javascript:accent_red(\'del\', \'' +
                            res[i][0].substr(0, res[i][2]) + '2' + res[i][0].substr(res[i][2], res[i][1] - res[i][2]) + '1' + res[i][0].substr(res[i][1]) + '\')"><span>' +
                            res[i][0].substr(0, res[i][2] + 1) + '&#768;' + res[i][0].substr(res[i][2] + 1, res[i][1] - res[i][2]) + '&#769;' + res[i][0].substr(res[i][1] + 1) + '</span>';
                    }
                } else {
                    temp += '<form method=post action="javascript:accent_red(\'del\', \'' +
                        res[i][0].substr(0, res[i][1]) + '1' + res[i][0].substr(res[i][1]) + '\')"> \
                        <span>' + res[i][0].substr(0, res[i][1] + 1) + '&#769;' + res[i][0].substr(res[i][1] + 1) + '</span>';
                }
                temp += '<input class="btn btn-outline-light btn-sm accent-del" type="submit" value="&#10008;" title="Удалить данное ударение"></form>';
            }
            document.getElementById('accent_dict').innerHTML = temp
        } else {
            for (i = 0; i < res.length; i++) {
                temp += '<form method=post action="javascript:dict_red(\'del\', \'' + res[i].replace('?', 'ё') + '\')">';
                temp += '<span>' + res[i].replace('?', 'ё') + '</span>';
                temp += '<input class="btn btn-outline-light btn-sm accent-del" type="submit" value="&#10008;" title="Удалить данное ударение"></form>';
            }
            document.getElementById('replace_dict').innerHTML = temp
        }
    }).fail(function () {
        console.log('fail')
    })
}


// Вспомогательное

function loaded() {
    /* 
     * функция при загрузке страницы
     */
    if (window.location.pathname == '/base/index' || window.location.pathname == '/base/') {
        paginate('all', 1);
        paginate('my', 1);
    } else if (window.location.pathname == '/base/dict_edit') {
        dict_trigger('acc');
        dict_trigger('rep');
    }
}


$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})


window.onload = loaded;