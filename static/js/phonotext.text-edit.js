// Функции страницы редактирования

function start() {
    /* 
     * подтверждение сохранения изменений анализа
     */
    var text = document.getElementById('text_ed').value,
        settings = [],
        cur_id = window.location.pathname.split('/');
    cur_id = cur_id[cur_id.length - 1];
    text = text.replace(/^[\s]*/g, '').replace(/[\s]*$/g, '').replace(/[\u0301\u0300]/g, '');

    settings[0] = document.getElementById('private').checked;
    settings[1] = document.getElementById('author-name').value;
    settings[2] = document.getElementById('text-name').value;
    settings[3] = document.getElementById('text-series').value;
    settings[4] = document.getElementById('text-year').value;
    settings[5] = [];
    settings[5][0] = document.getElementById('cons1').checked;
    settings[5][1] = document.getElementById('cons2').checked;
    settings[5][2] = document.getElementById('cons3').checked;
    settings[6] = [false, false];
    if (document.getElementById('comm1'))
    {
        settings[6][0] = document.getElementById('comm1').checked;
        settings[6][1] = document.getElementById('comm2').checked;
    }
    settings[8] = [];
    settings[8][0] = document.getElementById('choose-ias1').value;
    settings[8][1] = document.getElementById('choose-ias2').value;
    settings[8][2] = document.getElementById('choose-iasf').value;
    settings[9] = document.getElementById('lang').innerText;

    $.post('start/' + cur_id, {
        text: text,
        private: settings[0],
        author_name: settings[1],
        text_name: settings[2],
        text_series: settings[3],
        text_year: settings[4],
        cons1: settings[5][0],
        cons2: settings[5][1],
        cons3: settings[5][2],
        comm1: settings[6][0],
        comm2: settings[6][1],
        ias1: settings[8][0],
        ias2: settings[8][1],
        ias3: settings[8][2],
        lang: settings[9]
    }).done(function (response) {
        unsaved(0);
        window.location.href = window.location.pathname.replace('/edit', '/text');
    }).fail(function () {
        console.log('fail')
    })
}


function unsaved(value) {
    /* 
     * включение/выключение оповещения при уходе со страницы с несохранёнными данными
     * используется на /edit
     */
    if (window.location.pathname.match('/edit') != null) {
        if (value == 1) {
            unsaved_data = 1;
            document.getElementById('noname_button').disabled = false;
            document.getElementById('noname_button').style.opacity = 1;
        } else {
            unsaved_data = 0;
            document.getElementById('noname_button').disabled = true;
            document.getElementById('noname_button').style.opacity = .33;
        }
    }
}


// Общие функции

function trigger(response, chain_connect = false) {
    /* 
     * отображение результатов анализа
     */
    var res = JSON.parse(response);
    var str = '',
        vowels = res['syll'].map(function (syll) {
            return syll[1];
        });
    stat = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

    if (res == 'err2') {
        alert('Слишком длинный текст!');
    } else {
        console.log(res);
        // первый блок – повторы
        if (res['rep']) {
            for (o = 0; o < res['rep'].length; o++) {
                var i = 0,
                    last_elem = null;
                while (res['rep'][o][i]) {
                    if (res['rep'][o][i][0] == last_elem) {
                        res['rep'][o].splice(res['rep'][o].indexOf(res['rep'][o][i]), 1);
                    } else {
                        last_elem = res['rep'][o][i][0];
                        i++;
                    }
                }
            }

            str += '<tr><td class="sort sort-number active-down">№</td><td class="sort sort-chain">Цепь</td><td class="sort sort-ias">ИАС-Ф</td></tr>';
            for (i = res['rep'].length - 1; i >= 0; i--) {
                for (o = res['rep'][i].length - 1; o >= 0; o--) {
                    ias = 0;
                    if (!/[-]/.test(res['rep'][i][o][1])) {
                        ias += 2;
                    }
                    if (!/[|]/.test(res['rep'][i][o][1])) {
                        ias += 2;
                    }
                    if (res['lang'] != 'english') {
                        if (/[йцкнгшщзхфвпрлджчсмтб]+[|\-]*[уеыаоэяиюё][|\-]*[йцкнгшщзхфвпрлджчсмтб]+/.test(res['rep'][i][o][1])) {
                            ias += 3;
                        } else if (/[йцкнгшщзхфвпрлджчсмтб|\-]+[уеыаоэяиюё]/.test(res['rep'][i][o][1])) {
                            ias += 2;
                        } else if (/[уеыаоэяиюё][|\-йцкнгшщзхфвпрлджчсмтб]+/.test(res['rep'][i][o][1])) {
                            ias += 1;
                        } else {
                            console.log(res['rep'][i][o][1]);
                        }
                        if (!/[й]/.test(res['rep'][i][o][1])) {
                            ias += 3;
                        }
                    } else {
                        ias += 3;
                        if (/[bcdfghklmnpqrstvxyze|\-]+[au|ea|ee|eu|ie|oa|ou|oe|ai|i|e|a|o|u][|\-bcdfghklmnpqrstvxyze]+/.test(res['rep'][i][o][1])) {
                            ias += 3;
                        } else if (/[bcdfghklmnpqrstvxyze|\-]+[au|ea|ee|eu|ie|oa|ou|oe|ai|i|e|a|o|u]/.test(res['rep'][i][o][1])) {
                            ias += 2;
                        } else if (/[au|ea|ee|eu|ie|oa|ou|oe|ai|i|e|a|o|u][|\-bcdfghklmnpqrstvxyze]+/.test(res['rep'][i][o][1])) {
                            ias += 1;
                        } else {
                            console.log(res['rep'][i][o][1]);
                        }
                    }

                    if (ias < document.getElementById('choose-ias1').value) {
                        res['rep'][i][o].push(ias);
                        res['rep'][i].splice(res['rep'][i].indexOf(res['rep'][i][o]), 1);
                        if (res['rep'][i].length < 2) {
                            res['rep'].splice(res['rep'].indexOf(res['rep'][i]), 1);
                            break;
                        } else if (res['rep'][i].length == 2) {
                            if ((vowels.indexOf(res['rep'][i][1][0]) - vowels.indexOf(res['rep'][i][0][0])) < 2) {
                                res['rep'].splice(res['rep'].indexOf(res['rep'][i]), 1);
                                break;
                            }
                        }
                    } else {
                        res['rep'][i][o].push(ias);
                    }
                }
            }

            var del_elem = [];
            for (i = 0; i < res['rep'].length; i++) {
                for (k = i + 1; k < res['rep'].length; k++) {
                    relapse = false;
                    if (res['rep'][i].length == res['rep'][k].length) {
                        relapse = true;
                        for (l = 0; l < res['rep'][i].length; l++) {
                            if (res['rep'][i][l][1] !== res['rep'][k][l][1]) {
                                relapse = false;
                                break;
                            }
                        }
                    }
                    if (relapse) {
                        del_elem.push(parseInt(res['rep'].indexOf(res['rep'][i])));
                        break;
                    }
                }
            }
            
            for (i = del_elem.length - 1; i >= 0; --i) {
                res['rep'].splice(del_elem[i], 1);
            }
            for (i = 0; i < res['rep'].length; i++) {
                temp_str = '';


                var voic_cons = 0,
                    deaf_cons = 0,
                    assoc_count = { 'ш': 0, 'щ': 0, 'ж': 0, 'ч': 0, 'к': 0, 'г': 0, 'х': 0 },
                    cur_soft = 0,
                    soft_cons = 0,
                    solid_cons = 0,
                    vow_count = { 'а': 0, 'о': 0, 'у': 0, 'и': 0, 'е': 0 },
                    ias_2 = 0,
                    ias_f = 0;



                temp_str += '<tr class="chain"><td><button type="button" class="btn btn-sm btn-outline-secondary btn-underline underline';
                for (o = 0; o < res['rep'][i].length; o++) {
                    temp_str += '-' + res['rep'][i][o][0];
                }
                temp_str += '">' + (parseInt(i) + 1) + '</button></td><td>';
                count = 0;
                dist_count = 0;
                for (o = 0; o < res['rep'][i].length; o++) {
                    if (res['rep'][i][o + 1]) {
                        
                        var distance = vowels.indexOf(res['rep'][i][o + 1][0]) - vowels.indexOf(res['rep'][i][o][0]);

                        if (distance > 1) {
                            temp_str += ' <span class="rep base-' + res['rep'][i][o][0] + '" title="ИАС-1: ' + res['rep'][i][o][2] + '">' + res['rep'][i][o][1] + '</span>';
                            temp_str += ' <span class="rep-hyp hyp-' + res['rep'][i][o][0] + ' hyp-' + res['rep'][i][o + 1][0]
                                + '" title="Расстояние: ' + distance + '"> – </span>';
                            count++;
                            dist_count += distance;
                        } else {
                            var len_1 = (' ' + res['rep'][i][o][1]).slice(1).replace(/[^а-яёa-z]/g, ''),
                                len_2 = (' ' + res['rep'][i][o + 1][1]).slice(1).replace(/[^а-яёa-z]/g, '');
                            if (len_2.length > len_1.length) {
                                len_1 = res['rep'][i][o][1];
                                len_2 = res['rep'][i][o + 1][1];
                                test1 = 1;
                                while (len_2.slice(test1 - 1, test1).search(/[уеёэоаыяиюieaou]/) == -1) { test1++ }
                                test2 = 1;
                                while (len_1.slice(test2 * (-1)).search(/[уеёэоаыяиюieaou]/) == -1) { test2++ }
                                if (test2 > test1) {
                                    len_2 = len_2.slice(test1 - 1);
                                } else {
                                    len_2 = len_2.slice(test2 - 1);
                                }
                                temp_str += ' <span class="rep-hyp base-' + res['rep'][i][o][0] + ' base-' + res['rep'][i][o + 1][0]
                                    + ' hyp-' + res['rep'][i][o][0] + ' hyp-' + res['rep'][i][o + 1][0]
                                    + ' double" title="ИАС-1: ' + res['rep'][i][o][2] + '(' + res['rep'][i][o + 1][2] + ')">' + len_1 + '(' + len_2 + ')</span>';
                                if (res['rep'][i][o + 2]) {
                                    distance = vowels.indexOf(res['rep'][i][o + 2][0]) - vowels.indexOf(res['rep'][i][o + 1][0]);
                                    temp_str += ' <span class="rep-hyp hyp-' + res['rep'][i][o + 1][0] + ' hyp-' + res['rep'][i][o + 2][0]
                                        + '" title="Расстояние: ' + distance + '"> – </span>';
                                }
                                o++;
                            } else {
                                len_1 = res['rep'][i][o][1];
                                len_2 = res['rep'][i][o + 1][1];
                                test1 = 1;
                                while (len_2.slice(test1 - 1, test1).search(/[уеёэоаыяиюieaou]/) == -1) { test1++ }
                                test2 = 1;
                                while (len_1.slice(test2 * (-1)).search(/[уеёэоаыяиюieaou]/) == -1) { test2++ }
                                if (test2 > test1) {
                                    len_1 = len_1.slice(0, (test1 - 1) * -1);
                                } else {
                                    len_1 = len_1.slice(0, (test2 - 1) * -1);
                                }
                                temp_str += ' <span class="rep-hyp base-' + res['rep'][i][o][0] + ' base-' + res['rep'][i][o + 1][0]
                                    + ' hyp-' + res['rep'][i][o][0] + ' hyp-' + res['rep'][i][o + 1][0]
                                    + ' double" title="ИАС-1: (' + res['rep'][i][o][2] + ')' + res['rep'][i][o + 1][2] + '">(' + len_1 + ')' + len_2 + '</span>';
                                if (res['rep'][i][o + 2]) {
                                    distance = vowels.indexOf(res['rep'][i][o + 2][0]) - vowels.indexOf(res['rep'][i][o + 1][0]);
                                    temp_str += ' <span class="rep-hyp hyp-' + res['rep'][i][o + 1][0] + ' hyp-' + res['rep'][i][o + 2][0]
                                        + '" title="Расстояние: ' + distance + '"> – </span>';
                                }
                                o++;
                            }
                            count++;
                            dist_count += distance;
                        }
                    } else {
                        temp_str += ' <span class="rep base-' + res['rep'][i][o][0] + '" title="ИАС-1: ' + res['rep'][i][o][2] + '">' + res['rep'][i][o][1] + '</span>';
                    }
                }

                for (o = 0; o < res['rep'][i].length; o++) {
                    var main_elem = res['rep'][i][o][0],
                        inner = res['rep'][i][o][1],
                        vow = inner.search(/[ёеуэоаыяиюieaou]/),
                        prev_arr = [],
                        next_arr = [];

                    // определение массива выделения предыдущих элементов
                    for (k = 0; k < vow; k++) {
                        if (inner[k].match(/[-|]/)) {
                            prev_arr.unshift(0);
                        } else {
                            prev_arr.unshift(1);
                        }
                    }

                    // определение массива выделения следующих элементов
                    for (k = inner.length - 1; k > vow; k--) {
                        if (inner[k].match(/[-|]/)) {
                            next_arr.unshift(0);
                        } else {
                            next_arr.unshift(1);
                        }
                    }

                    var base_fs = '',
                        prev_i = 1;
                    for (k = 0; k < prev_arr.length; k++) {
                        while (res['base'][main_elem - prev_i].replace(/[\u0301\u0300]/g, '').match(/[^а-щыэюяяa-zё ]/i) != null) {
                            prev_i++;
                        }
                        if (prev_arr[k]) {
                            base_fs += res['base'][main_elem - prev_i].replace(/[\u0301\u0300]/g, '');
                        }
                        prev_i++;
                    }

                    base_fs = base_fs.split('').reverse().join().replace(/,/g, '');

                    if (prev_arr.length && res['base'][main_elem - prev_i + 1] && res['base'][main_elem - prev_i + 1].replace(/[\u0301\u0300]/g, '').match(/[еёюя]/)) {
                        base_fs = base_fs.slice(0, base_fs.length - 1);
                        base_fs += 'й';
                    }

                    base_fs += res['base'][main_elem].replace(/[\u0301\u0300]/g, '');

                    var next_i = 1;
                    for (k = 0; k < next_arr.length; k++) {
                        while (res['base'][main_elem + next_i].replace(/[\u0301\u0300]/g, '').match(/[^а-щыэюяяa-zё ]/i) != null) {
                            next_i++;
                        }
                        if (next_arr[k]) {
                            base_fs += res['base'][main_elem + next_i].replace(/[\u0301\u0300]/g, '');
                        }
                        next_i++;
                    }
                    if (next_arr.length && res['base'][main_elem + next_i - 1] && res['base'][main_elem + next_i - 1].replace(/[\u0301\u0300]/g, '').match(/[еёюя]/i)) {
                        base_fs = base_fs.slice(0, base_fs.length - 1);
                        base_fs += 'й';
                    } else if (next_arr.length && res['base'][main_elem + next_i] && res['base'][main_elem + next_i].replace(/[\u0301\u0300]/g, '').match(/[иеёюя]/i)) {
                        base_fs += "'";
                    }


                    if (res['lang'] != 'english') {
                        voic_cons += base_fs.match(/[бвдз]/gi) ? base_fs.match(/[бвдз]/gi).length : 0;
                        deaf_cons += base_fs.match(/[пфтс]/gi) ? base_fs.match(/[пфтс]/gi).length : 0;
                        sonor_match = base_fs.match(/[лмнр]/gi) ? base_fs.match(/[лмнр]/gi).length : 0;
                        if (sonor_match > 0) {
                            voic_cons += sonor_match;
                        } else {
                            deaf_cons++;
                        }
                        assoc_count['ш'] += base_fs.match(/ш/gi) ? base_fs.match(/ш/gi).length : 0;
                        assoc_count['щ'] += base_fs.match(/щ/gi) ? base_fs.match(/щ/gi).length : 0;
                        assoc_count['ж'] += base_fs.match(/ж/gi) ? base_fs.match(/ж/gi).length : 0;
                        assoc_count['ч'] += base_fs.match(/ч/gi) ? base_fs.match(/ч/gi).length : 0;
                        assoc_count['к'] += base_fs.match(/к/gi) ? base_fs.match(/к/gi).length : 0;
                        assoc_count['г'] += base_fs.match(/г/gi) ? base_fs.match(/г/gi).length : 0;
                        assoc_count['х'] += base_fs.match(/х/gi) ? base_fs.match(/х/gi).length : 0;

                        cur_soft = base_fs.match(/[бвгдзклмнпрстфх][иеёюя]/gi) ? base_fs.match(/[бвгдзклмнпрстфх][иеёюя]/gi).length : 0;
                        cur_soft += base_fs.match(/'/gi) ? 1 : 0;
                        soft_cons += cur_soft;
                        solid_cons += (base_fs.match(/[бвгдзклмнпрстфх]/gi) ? base_fs.match(/[бвгдзклмнпрстфх]/gi).length : 0) - cur_soft;


                        vow_count['а'] += base_fs.match(/[ая]/i) ? 1 : 0;
                        vow_count['о'] += base_fs.match(/[оё]/i) ? 1 : 0;
                        vow_count['у'] += base_fs.match(/[ую]/i) ? 1 : 0;
                        vow_count['и'] += base_fs.match(/[иы]/i) ? 1 : 0;
                        vow_count['е'] += base_fs.match(/[еэ]/i) ? 1 : 0;
                    }

                    ias_2 += res['rep'][i][o][2];
                }

                ias_2 /= res['rep'][i].length;
                base_ias_2 = ias_2;
                ias_2 = Math.round(ias_2);

                if (res['lang'] != 'english') {
                    if (voic_cons != 0 && deaf_cons != 0) {
                        if ((voic_cons >= deaf_cons) && ((deaf_cons / voic_cons) >= 0.2)) {
                            ias_2 -= 3;
                        } else if ((deaf_cons > voic_cons) && ((voic_cons / deaf_cons) >= 0.2)) {
                            ias_2 -= 3;
                        }
                    }

                    if (!((assoc_count['ш'] >= assoc_count['щ'] + assoc_count['ж'] + assoc_count['ч'])
                        || (assoc_count['щ'] >= assoc_count['ш'] + assoc_count['ж'] + assoc_count['ч'])
                        || (assoc_count['ж'] >= assoc_count['ш'] + assoc_count['щ'] + assoc_count['ч'])
                        || (assoc_count['ч'] >= assoc_count['ш'] + assoc_count['щ'] + assoc_count['ж']))) {
                        ias_2 -= 2;
                    } else if (!((assoc_count['к'] >= assoc_count['г'] + assoc_count['х'])
                        || (assoc_count['г'] >= assoc_count['к'] + assoc_count['х'])
                        || (assoc_count['х'] >= assoc_count['к'] + assoc_count['г']))) {
                        ias_2 -= 2;
                    }

                    if (soft_cons != 0 && solid_cons != 0) {
                        if ((soft_cons >= solid_cons) && ((solid_cons / soft_cons) >= 0.2)) {
                            ias_2 -= 1;
                        } else if ((solid_cons > soft_cons) && ((soft_cons / solid_cons) >= 0.2)) {
                            ias_2 -= 1;
                        }
                    }
                }

                ias_f = ias_2;

                if (res['lang'] != 'english') {
                    if (((vow_count['а'] / 2) > (vow_count['о'] + vow_count['у'] + vow_count['и'] + vow_count['е']))
                        || ((vow_count['о'] / 2) > (vow_count['а'] + vow_count['у'] + vow_count['и'] + vow_count['е']))
                        || ((vow_count['у'] / 2) > (vow_count['а'] + vow_count['о'] + vow_count['и'] + vow_count['е']))
                        || ((vow_count['и'] / 2) > (vow_count['а'] + vow_count['о'] + vow_count['у'] + vow_count['е']))
                        || ((vow_count['е'] / 2) > (vow_count['а'] + vow_count['о'] + vow_count['у'] + vow_count['и']))) {
                        ias_f += 3;
                    } else if ((vow_count['а'] > (vow_count['о'] + vow_count['у'] + vow_count['и'] + vow_count['е']))
                        || (vow_count['о'] > (vow_count['а'] + vow_count['у'] + vow_count['и'] + vow_count['е']))
                        || (vow_count['у'] > (vow_count['а'] + vow_count['о'] + vow_count['и'] + vow_count['е']))
                        || (vow_count['и'] > (vow_count['а'] + vow_count['о'] + vow_count['у'] + vow_count['е']))
                        || (vow_count['е'] > (vow_count['а'] + vow_count['о'] + vow_count['у'] + vow_count['и']))) {
                        ias_f += 2;
                    } else if (((vow_count['а'] * 1.5) > (vow_count['о'] + vow_count['у'] + vow_count['и'] + vow_count['е']))
                        || ((vow_count['о'] * 1.5) > (vow_count['а'] + vow_count['у'] + vow_count['и'] + vow_count['е']))
                        || ((vow_count['у'] * 1.5) > (vow_count['а'] + vow_count['о'] + vow_count['и'] + vow_count['е']))
                        || ((vow_count['и'] * 1.5) > (vow_count['а'] + vow_count['о'] + vow_count['у'] + vow_count['е']))
                        || ((vow_count['е'] * 1.5) > (vow_count['а'] + vow_count['о'] + vow_count['у'] + vow_count['и']))) {
                        ias_f += 1;
                    }
                }


                if (ias_f < document.getElementById('choose-iasf').value || ias_2 < document.getElementById('choose-ias2').value) {
                    res['rep'].splice(res['rep'].indexOf(res['rep'][i]), 1);
                    i--;
                    continue;
                }
                str += temp_str;



                for (o = 0; o < res['rep'][i].length; o++) {
                    ind = res['syll'].map(function (x) { return x[1] });
                    if (res['syll'][ind.indexOf(res['rep'][i][o][0])][2]) {
                        res['syll'][ind.indexOf(res['rep'][i][o][0])][2] += ias_2;
                        res['syll'][ind.indexOf(res['rep'][i][o][0])][3] += ias_f;
                        res['syll'][ind.indexOf(res['rep'][i][o][0])][4] += 1;
                    } else {
                        res['syll'][ind.indexOf(res['rep'][i][o][0])][2] = ias_2;
                        res['syll'][ind.indexOf(res['rep'][i][o][0])][3] = ias_f;
                        res['syll'][ind.indexOf(res['rep'][i][o][0])][4] = 1;
                    }
                }

                ru_temp = '';
                if (res['lang'] != 'english') {
                    ru_temp = '; Звонкие/глухие: ' + voic_cons + '/' + deaf_cons
                        + '; Мягкие/твёрдые: ' + soft_cons + '/' + solid_cons
                        + '; Различие ш-щ-ж-ч: ' + assoc_count['ш'] + '/' + assoc_count['щ'] + '/' + assoc_count['ж'] + '/' + assoc_count['ч']
                        + '; Различие к-г-х: ' + assoc_count['к'] + '/' + assoc_count['г'] + '/' + assoc_count['х']
                        + '; Различие а-о-у-е-и: ' + vow_count['а'] + '/' + vow_count['о'] + '/' + vow_count['у'] + '/' + vow_count['е'] + '/' + vow_count['и'];
                }
                str += '</td><td title="Элементов в цепи: ' + (parseInt(count) + 1)
                    + '; Среднее расстояние: ' + ((dist_count / count).toFixed(2) * 100 / 100)
                    + '; Средний ИАС1: ' + (base_ias_2.toFixed(2) * 100 / 100)
                    + '; ИАС2: ' + ias_2
                    + '; ИАСФ: ' + ias_f
                    + ru_temp
                    + '">' + ias_f + '</td></tr>';
                if (!document.getElementById('group_chain').parentNode.classList.contains('active')) {
                    stat[3] += ias_f;
                    stat[6] += (parseInt(count) + 1);
                    stat[7] += ((dist_count / count).toFixed(2) * 100 / 100);
                    stat[8] += (base_ias_2.toFixed(2) * 100 / 100);
                    stat[9] += ias_2;
                    if (res['lang'] != 'english') {
                        stat[10] += voic_cons;
                        stat[11] += deaf_cons;
                        stat[12] += soft_cons;
                        stat[13] += solid_cons;
                        stat[14] += assoc_count['ш'];
                        stat[15] += assoc_count['щ'];
                        stat[16] += assoc_count['ж'];
                        stat[17] += assoc_count['ч'];
                        stat[18] += assoc_count['к'];
                        stat[19] += assoc_count['г'];
                        stat[20] += assoc_count['х'];
                        stat[21] += vow_count['а'];
                        stat[22] += vow_count['о'];
                        stat[23] += vow_count['у'];
                        stat[24] += vow_count['е'];
                        stat[25] += vow_count['и'];
                    }
                }
            }
        }


        var myNode = document.getElementById('all');
        try {
            while (myNode.firstChild) {
                myNode.removeChild(myNode.firstChild);
            }
        } catch (e) { }

        var div = document.createElement('table');
        div.innerHTML = str;
        document.getElementById('all').appendChild(div);

        if (chain_connect) {
            chain_chains = [];

            for (o = 0; o < res['rep'].length; o++) {
                var o_indexes = res['rep'][o].map(function (elem) { return elem[0] }),
                    main_pos = o,
                    longest = -1,
                    same_chains = [];

                for (i = o; i < res['rep'].length; i++) {
                    var i_indexes = res['rep'][i].map(function (elem) { return elem[0] }),
                        add_pos = i,
                        excess = [],
                        cont = 1;
                    if ((i_indexes.length + o_indexes.length) > 4) {
                        for (k = 0; k < i_indexes.length; k++) {
                            if (o_indexes.indexOf(i_indexes[k]) == -1) {
                                excess.push(i_indexes[k]);
                            }
                        }
                        if (i_indexes.length > 2 && o_indexes.length > 2 && excess.length < 2) {
                            same_chains.push(i);
                            if (longest == -1) {
                                longest = i;
                            } else if (i_indexes.length > res['rep'][longest].length) {
                                longest = i;
                            }
                        } else if ((i_indexes.length == 2 || o_indexes.length == 2) && excess.length == 0) {
                            same_chains.push(i);
                        }
                    }
                }
                if (same_chains.length > 2) {
                    for (k = 0; k < chain_chains.length; k++) {
                        relapse_k = 0;
                        relapse_l = 0;
                        for (l = 0; l < chain_chains[k][1].length; l++) {
                            if (same_chains.indexOf(chain_chains[k][1][l]) == -1) {
                                relapse_l++;
                            }
                        }
                        for (l = 0; l < same_chains.length; l++) {
                            if (chain_chains[k][1].indexOf(same_chains[l]) == -1) {
                                relapse_k++;
                            }
                        }
                        if (relapse_k == 0) {
                            cont = -1;
                            break;
                        } else if (relapse_l == 0) {
                            cont = 0;
                            break;
                        }
                    }
                    if (cont == 1) {
                        chain_chains.push([longest, same_chains]);
                    } else if (cont == 0) {
                        chain_chains[k] == [longest, same_chains];
                    }
                }
            }

            function compareNumbers(a, b) {
                return a - b;
            }

            del_elems = chain_chains.join(',').split(',').map(function (elem) { return parseInt(elem); }).filter((v, i, a) => a.indexOf(v) === i).sort(compareNumbers);
            main_elems = chain_chains.map(function (elem) { return elem[0]; })

            main = document.getElementById('all').childNodes[0].childNodes[0].cloneNode(true);
            copy = document.createElement('tbody');
            copy.appendChild(main.childNodes[0].cloneNode(true));


            for (i = 0; i < document.getElementsByClassName('chain').length; i++) {
                if (del_elems.indexOf(i) != -1 && main_elems.indexOf(i) != -1) {
                    var ias = 0,
                        count = 0;
                    multichain = main.getElementsByClassName('chain')[i].cloneNode(true);
                    multichain.classList.add('multi');
                    multichain.classList.add('par-' + i);
                    multichain.childNodes[1].classList.add('accordion-toggle');
                    multichain.childNodes[1].setAttribute('data-toggle', 'collapse');
                    multichain.childNodes[1].setAttribute('data-target', '.multi-' + i);
                    multichain.childNodes[2].classList.add('accordion-toggle');
                    multichain.childNodes[2].setAttribute('data-toggle', 'collapse');
                    multichain.childNodes[2].setAttribute('data-target', '.multi-' + i);
                    for (o = 0; o < chain_chains[main_elems.indexOf(i)][1].length; o++) {
                        if (chain_chains[main_elems.indexOf(i)][1][o] == chain_chains[main_elems.indexOf(i)][0]) { continue; }
                        ias += parseInt(main.getElementsByClassName('chain')[chain_chains[main_elems.indexOf(i)][1][o]].childNodes[2].innerText);
                        count++;
                    }
                    multichain.childNodes[2].innerText = (ias / count).toFixed(0);
                    copy.appendChild(multichain);
                    for (o = 0; o < chain_chains[main_elems.indexOf(i)][1].length; o++) {
                        if (chain_chains[main_elems.indexOf(i)][1][o] == chain_chains[main_elems.indexOf(i)][0]) { continue; }
                        multichain = main.getElementsByClassName('chain')[chain_chains[main_elems.indexOf(i)][1][o]].cloneNode(true);
                        multichain.classList.add('accordion-body');
                        multichain.classList.add('collapse');
                        multichain.classList.add('multi-' + i);
                        copy.appendChild(multichain);
                    }

                } else if (del_elems.indexOf(i) == -1) {
                    multichain = main.getElementsByClassName('chain')[i].cloneNode(true);
                    copy.appendChild(multichain);
                }
            }
            document.getElementById('all').childNodes[0].replaceChild(copy, document.getElementById('all').childNodes[0].childNodes[0]);
        }
        
        // третий блок – sp(max)
        ////////////////////////////////////
        chain_chains = [];

        for (o = 0; o < res['rep'].length; o++) {
            var o_indexes = res['rep'][o].map(function (elem) { return elem[0] }),
                main_pos = o,
                longest = -1,
                same_chains = [];

            for (i = o; i < res['rep'].length; i++) {
                var i_indexes = res['rep'][i].map(function (elem) { return elem[0] }),
                    add_pos = i,
                    excess = [],
                    cont = 1;
                if ((i_indexes.length + o_indexes.length) > 4) {
                    for (k = 0; k < i_indexes.length; k++) {
                        if (o_indexes.indexOf(i_indexes[k]) == -1) {
                            excess.push(i_indexes[k]);
                        }
                    }
                    if (i_indexes.length > 2 && o_indexes.length > 2 && excess.length < 2) {
                        same_chains.push(i);
                        if (longest == -1) {
                            longest = i;
                        } else if (i_indexes.length > res['rep'][longest].length) {
                            longest = i;
                        }
                    } else if ((i_indexes.length == 2 || o_indexes.length == 2) && excess.length == 0) {
                        same_chains.push(i);
                    }
                }
            }
            if (same_chains.length > 2) {
                for (k = 0; k < chain_chains.length; k++) {
                    relapse_k = 0;
                    relapse_l = 0;
                    for (l = 0; l < chain_chains[k][1].length; l++) {
                        if (same_chains.indexOf(chain_chains[k][1][l]) == -1) {
                            relapse_l++;
                        }
                    }
                    for (l = 0; l < same_chains.length; l++) {
                        if (chain_chains[k][1].indexOf(same_chains[l]) == -1) {
                            relapse_k++;
                        }
                    }
                    if (relapse_k == 0) {
                        cont = -1;
                        break;
                    } else if (relapse_l == 0) {
                        cont = 0;
                        break;
                    }
                }
                if (cont == 1) {
                    chain_chains.push([longest, same_chains]);
                } else if (cont == 0) {
                    chain_chains[k] == [longest, same_chains];
                }
            }
        }

        function compareNumbers(a, b) {
            return a - b;
        }

        del_elems = chain_chains.join(',').split(',').map(function (elem) { return parseInt(elem); }).filter((v, i, a) => a.indexOf(v) === i).sort(compareNumbers);
        main_elems = chain_chains.map(function (elem) { return elem[0]; })
        chains = document.getElementsByClassName('chain');
        /////////////////////////////////////////////
        if (!stat[0]) {
            stat[0] = document.getElementsByClassName('chain').length;
            stat[1] = chain_chains.length;
            stat[2] = document.getElementsByClassName('chain').length - del_elems.length;
            stat[4] = stat[5] = 0;
            for (i = 0; i < chain_chains.length; i++) {
                if (stat[4] < chain_chains[i][1].length) {
                    stat[4] = chain_chains[i][1].length;
                    stat[5] = chain_chains[i][0];
                }
            }
        }
        str = '<ul class="list-group text-center">';
        str += '<li class="list-group-item">Всего цепочек в тексте <br> ' + stat[0] + '</li>';
        str += '<li class="list-group-item">Собрано групп <br> ' + stat[1] + '</li>';
        str += '<li class="list-group-item">Одиночных цепей <br> ' + stat[2] + '</li>';
        str += '<li class="list-group-item">Средний ИАС-Ф цепей <br> ' + (stat[3] / stat[0]).toFixed(2) + '</li>';
        str += '<li class="list-group-item">Наибольшее количество элементов в группе ' + stat[4] + '<br>  Начинается с цепи №' + stat[5] + '</li>';
        str += '<li class="list-group-item">Среднее количество элементов в цепи <br> ' + (stat[6] / stat[0]).toFixed(2) + '</li>';
        str += '<li class="list-group-item">Среднее расстояние между элементами цепей<br> ' + (stat[7] / stat[0]).toFixed(2) + '</li>';
        str += '<li class="list-group-item">Средний ИАС-1 элементов <br> ' + (stat[8] / stat[0]).toFixed(2) + '</li>';
        str += '<li class="list-group-item">Средний промежуточный ИАС-2 цепей <br> ' + (stat[9] / stat[0]).toFixed(2) + '</li>';
        if (res['lang'] != 'english') {
            str += '<li class="list-group-item">Отношение звонких согласных к глухим <br> ' + (stat[10] / stat[11]).toFixed(2) + ' (' + stat[10] + '/' + stat[11] + ')</li>';
            str += '<li class="list-group-item">Отношение мягких согласных к твёрдым <br> ' + (stat[12] / stat[13]).toFixed(2) + ' (' + stat[12] + '/' + stat[13] + ')</li>';
            str += '<li class="list-group-item">Соотношение ш-щ-ж-ч в элементах <br> ' + stat[14] + '/' + stat[15] + '/' + stat[16] + '/' + stat[17] + '</li>';
            str += '<li class="list-group-item">Соотношение ш-щ-ж-ч в тексте <br> '
                + (res['base'].match(/ш/g) ? res['base'].match(/ш/g).length : 0) + '/'
                + (res['base'].match(/щ/g) ? res['base'].match(/щ/g).length : 0) + '/'
                + (res['base'].match(/ж/g) ? res['base'].match(/ж/g).length : 0) + '/'
                + (res['base'].match(/ч/g) ? res['base'].match(/ч/g).length : 0) + '</li>';
            str += '<li class="list-group-item">Соотношение к-г-х в элементах <br> ' + stat[18] + '/' + stat[19] + '/' + stat[20] + '</li>';
            str += '<li class="list-group-item">Соотношение к-г-х в тексте <br> '
                + (res['base'].match(/к/g) ? res['base'].match(/к/g).length : 0) + '/'
                + (res['base'].match(/г/g) ? res['base'].match(/г/g).length : 0) + '/'
                + (res['base'].match(/х/g) ? res['base'].match(/х/g).length : 0) + '</li>';
            str += '<li class="list-group-item">Соотношение звуков а-о-у-е-и в элементах <br> ' + stat[21] + '/' + stat[22] + '/' + stat[23] + '/' + stat[24] + '/' + stat[25] + '</li>';
            str += '<li class="list-group-item">Соотношение звуков а-о-у-е-и в тексте <br> '
                + (res['base'].match(/а/g) ? res['base'].match(/а/g).length : 0) + '/'
                + (res['base'].match(/о/g) ? res['base'].match(/о/g).length : 0) + '/'
                + (res['base'].match(/у/g) ? res['base'].match(/у/g).length : 0) + '/'
                + (res['base'].match(/е/g) ? res['base'].match(/е/g).length : 0) + '/'
                + (res['base'].match(/и/g) ? res['base'].match(/и/g).length : 0) + '</li>';
        }
        str += '</ul>';
        need_stat = false;


        var myNode = document.getElementById('two');
        try {
            while (myNode.firstChild) {
                myNode.removeChild(myNode.firstChild);
            }
        } catch (e) { }

        var div = document.createElement('div');
        div.innerHTML = str;
        document.getElementById('two').appendChild(div);

        // четвёртый блок – акценты
        str = '';
        var re = /[аоуыиэеёюяАОУЫИЭЕЁЮЯ]/;
        if (window.location.pathname.search('/text/') == -1) {
            
            // —— отображение слов с отсутствующими акцентами для данного текста
            count = 0;
            for (i = 0; i < res['accents'][0].length; i++) {
                if ((res['accents'][0][i][0].search(re) != -1) && (res['accents'][0][i][2].length == 0)) {
                    if (count == 0) {
                        str += '<div id="accordionTwo"><div class="card"><div class="btn btn-light" data-toggle="collapse" data-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo" id="headingTwo"> \
                                <span>Нет ударений в словаре</span></div> \
                                <div id="collapseTwo" class="collapse" aria-labelledby="headingTwo" data-parent="#accordionTwo"><div class="card-body">';
                        count = 1;
                    }
                    temp_num = '';
                    for (o = 0; o < res['accents'][0][i][0].length; o++) {
                        temp_num += ' base-' + (res['accents'][0][i][1] + o);
                    }
                    str += '<form class="acc-choose acc-' + res['accents'][0][i][1] + '" method=post action="javascript:add_accent('
                        + res['accents'][0][i][1] + ', \'' + res['accents'][0][i][0] + '\')">';
                    str += '<span class="base' + temp_num + ' acc-list">' + res['accents'][0][i][0] + '</span>';
                    str += '<input class="btn btn-outline-light btn-sm accent-del" type="submit" value="+" title="Добавить ударение"></form>';
                }
            }
            if (count == 1) {
                str += '</div></div></div></div>';
            }

            // —— отображение слов с несколькими вариантами акцентов
            count = 0;
            for (i = 0; i < res['accents'][0].length; i++) {
                try {
                    if (res['accents'][0][i][0].search(re) != -1) {
                        if (Array.isArray(res['accents'][0][i][2][1])) {
                            if (count == 0) {
                                str += '<div id="accordion-accent"><div class="card"><div class="btn btn-light" data-toggle="collapse" \
                                        data-target="#collapseAccent" aria-expanded="true" aria-controls="collapseAccent" id="accent-heading"> \
                                        <span title="В словаре содержится несколько вариантов ударений. Выберите подходящее для данного текста.">Варианты ударений</span></div> \
                                        <div id="collapseAccent" class="collapse show" aria-labelledby="accent-heading" data-parent="#accordion-accent"><div class="card-body">';
                                count = 1;
                            }
                            str += '<div class="btn-group accent-choose">';
                            try {
                                for (o = 0; o < res['accents'][0].length; o++) {
                                    if (res['accents'][0][i][2][o][1] != null) {
                                        if (res['accents'][0][i][2][o][0] < res['accents'][0][i][2][o][1]) {
                                            temp = res['accents'][0][i][0].substring(0, res['accents'][0][i][2][o][0] + 1) +
                                                '&#768;' + res['accents'][0][i][0].substring(res['accents'][0][i][2][o][0] + 1, res['accents'][0][i][2][o][1] + 1) +
                                                '&#769;' + res['accents'][0][i][0].substring(res['accents'][0][i][2][o][1] + 1);
                                        } else {
                                            temp = res['accents'][0][i][0].substring(0, res['accents'][0][i][2][o][1] + 1) +
                                                '&#768;' + res['accents'][0][i][0].substring(res['accents'][0][i][2][o][1] + 1, res['accents'][0][i][2][o][0] + 1) +
                                                '&#769;' + res['accents'][0][i][0].substring(res['accents'][0][i][2][o][0] + 1);
                                        }
                                    } else {
                                        temp = res['accents'][0][i][0].substring(0, res['accents'][0][i][2][o][0] + 1) +
                                            '&#769;' + res['accents'][0][i][0].substring(res['accents'][0][i][2][o][0] + 1);
                                    }
                                    temp_num = ' base-' + (res['accents'][0][i][1] + res['accents'][0][i][2][o][0]);
                                    if (res['accents'][0][i][2][o][1]) {
                                        temp_num += ' base-' + (res['accents'][0][i][1] + res['accents'][0][i][2][o][1]);
                                    }
                                    str += '<form action="javascript: add_temp(\'' + res['accents'][0][i][0] + '\', ' + res['accents'][0][i][2][o][0] +
                                        ', ' + res['accents'][0][i][2][o][1] + ', ' + res["accents"][0][i][1] +
                                        ')"><input class="base' + temp_num + ' btn btn-light btn-sm" type="submit" Value="' + temp + '"></form>';
                                }
                            } catch (e) { }
                            str += '</div></br>';
                        }
                    }
                } catch (e) { }
            }
            if (count == 1) {
                str += '</div></div></div></div>';
            }

        }
        
        // —— отображение слов с изменёнными акцентами для данного текста
        count = 0;
        keys = Object.keys(res['custom']);
        values = Object.values(res['custom']);
        for (i = 0; i < keys.length; i++) {
            val = Array.from(values[i]);
            if (val.length) {
                if (count == 0) {
                    str += '<div id="accordionOne"><div class="card"><div class="btn btn-light" data-toggle="collapse" \
                            data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne" id="headingOne"> \
                            <span>Изменённые ударения</span></div> \
                            <div id="collapseOne" class="collapse show" aria-labelledby="headingOne" data-parent="#accordionOne"><div class="card-body">';
                    count = 1;
                }

                main_pos = parseInt(val[0][0]);
                acc_pos = parseInt(val[0][1]);
                add_pos = parseInt(val[0][2]);

                str += '<form method=post action="javascript:del_custom(\'' + keys[i] + '\', ' + main_pos + ')">';
                if (add_pos) {
                    temp_num = ' base-' + (main_pos + acc_pos) + ' base-' + (main_pos + add_pos);
                    if (add_pos > acc_pos) {
                        str += '<span class="base' + temp_num + ' acc-list">'
                            + keys[i].substr(0, acc_pos + 1) + '&#769;'
                            + keys[i].substr(acc_pos + 1, add_pos - acc_pos) + '&#768;'
                            + keys[i].substr(add_pos + 1)
                            + '</span>'
                    } else {
                        str += '<span class="base' + temp_num + ' acc-list">'
                            + keys[i].substr(0, add_pos + 1) + '&#768;'
                            + keys[i].substr(add_pos + 1, acc_pos - add_pos) + '&#769;'
                            + keys[i].substr(acc_pos + 1)
                            + '</span>'
                    }
                } else {
                    temp_num = ' base-' + (main_pos + acc_pos);
                    str += '<span class="base' + temp_num + ' acc-list">' + keys[i].substr(0, acc_pos + 1) + '&#769;' + keys[i].substr(acc_pos + 1) + '</span>'
                }
                if (window.location.pathname.search('/text/') == -1) {
                    str += '<input class="btn btn-outline-light btn-sm accent-del" type="submit" value="&#10008;" title="Удалить данное ударение"></form>';
                } else {
                    str += '</form>';
                }
            }
        }

        if (count == 1) {
            str += '</div></div></div></div>';
        }

        if (str == '') {
            str += 'В этом тексте нет изменённых ударений';
        }
        var myNode = document.getElementById('three');
        try {
            while (myNode.firstChild) {
                myNode.removeChild(myNode.firstChild);
            }
        } catch (e) { }
        var div = document.createElement('div');
        div.classList += 'text-center';
        div.innerHTML = str;
        document.getElementById('three').appendChild(div);

        // отображение базового текста рядом с полем ввода
        var count = -1;
        str = '';
        res['lines'].forEach(function (line) {
            line.forEach(function (syll) {
                if (syll[1] == 1) {
                    count++;
                    if (res['syll'][count]) {
                        chain_affil = '';
                        var ias_count = 0,
                            ias_sum = 0;
                        for (i = 0; i < res['rep'].length; i++) {
                            for (o = 0; o < res['rep'][i].length; o++) {
                                if (res['rep'][i][o][0] == res['syll'][count][1]) {
                                    chain_affil += (i + 1);
                                    ias_sum += res['rep'][i][o][2];
                                    ias_count++;
                                    plus = 1;
                                    while (1) {
                                        temp = 0;
                                        if (res['rep'][i + plus]) {
                                            for (o = 0; o < res['rep'][i + plus].length; o++) {
                                                if (res['rep'][i + plus][o][0] == res['syll'][count][1]) {
                                                    ias_sum += res['rep'][i + plus][o][2];
                                                    ias_count++;
                                                    plus++;
                                                    temp = 1;
                                                    break;
                                                }
                                            }
                                        }
                                        if (temp == 1) {
                                            continue;
                                        } else {
                                            if (plus > 1) {
                                                chain_affil += '–' + (i + plus);
                                                i += plus;
                                                break;
                                            } else {
                                                i++;
                                                break;
                                            }
                                        }
                                    }
                                    chain_affil += ', ';
                                    break;
                                }
                            }
                        }
                        if (chain_affil == '') {
                            title = 'Данный потенциальный слог не входит ни в одну цепочку.';
                        } else {
                            title = 'Данный потенциальный слог входит в следующие цепочки: ' + chain_affil.slice(0, -2);
                        }
                        str += '<span title="' + title + '" ias1="' + ((ias_sum / ias_count).toFixed(2) * 100 / 100) + '" ias2="'
                            + ((res['syll'][count][2] / res['syll'][count][4]).toFixed(2) * 100 / 100) + '" iasf="'
                            + ((res['syll'][count][3] / res['syll'][count][4]).toFixed(2) * 100 / 100) + '" chains="'
                            + ias_count + '" class="base base-' + res['syll'][count][1] + '">' + syll[0];
                        if (res['accents'][1].includes(res['syll'][count][1])) {
                            str += '<span class="accent">&#769;</span>';
                        }
                        if (res['accents'][2].includes(res['syll'][count][1])) {
                            str += '<span class="accent">&#768;</span>';
                        }
                        str += '</span>';
                    }
                } else {
                    str += '<span class="base base--1">' + syll[0] + '</span>';
                }
            });
            str += '<br>';
            count++;
        });
        try {
            document.getElementById('inter_text').innerHTML = str;
        } catch (e) { }

        sort_elems = document.getElementsByClassName('sort');
        for (k = 0; k < sort_elems.length; k++) {
            sort_elems[k].onclick = sort;
        }

        color_rules();
    }
}


function inter_analyze(first = false) {
    /* 
     * обновление результата анализа, при изменении текста или его настроек
     * в text используется только для первичного отображения
     */
    try {
        clear_highlight();
    } catch { }

    if (!first) {
        unsaved(1);
    }
    settings = [];
    if (window.location.pathname.search('/text/') == -1) {
        settings[0] = document.getElementById('private').checked;
        settings[1] = document.getElementById('author-name').value;
        settings[2] = document.getElementById('text-name').value;
        settings[3] = document.getElementById('text-series').value;
        settings[4] = document.getElementById('text-year').value;
    } else {
        settings[0] = 'true';
        settings[1] = '';
        settings[2] = '';
        settings[3] = '';
        settings[4] = '';
    }
    settings[9] = document.getElementById('lang').innerText;
    settings[5] = [];
    settings[5][0] = document.getElementById('cons1').checked;
    settings[5][1] = document.getElementById('cons2').checked;
    settings[5][2] = document.getElementById('cons3').checked;
    settings[6] = [];
    if (settings[9] == 'russian') {
        settings[6][0] = document.getElementById('comm1').checked;
        settings[6][1] = document.getElementById('comm2').checked;
    } else {
        settings[6][0] = false;
        settings[6][1] = false;
    }
    settings[7] = document.getElementById('group_chain').checked;
    settings[8] = [];
    settings[8][0] = document.getElementById('choose-ias1').value;
    settings[8][1] = document.getElementById('choose-ias2').value;
    settings[8][2] = document.getElementById('choose-iasf').value;
    if (!settings[5][0] && !settings[5][1] && !settings[5][2]) {
        document.getElementById('cons1').parentElement.style.backgroundColor = '#FF7F50';
        document.getElementById('cons2').parentElement.style.backgroundColor = '#FF7F50';
        document.getElementById('cons3').parentElement.style.backgroundColor = '#FF7F50';
    } else {
        document.getElementById('cons1').parentElement.style.backgroundColor = '';
        document.getElementById('cons2').parentElement.style.backgroundColor = '';
        document.getElementById('cons3').parentElement.style.backgroundColor = '';

        cur_id = window.location.pathname.split('/');
        cur_id = cur_id[cur_id.length - 1];

        if (window.location.pathname.search('/text/') == -1) {
            var text = document.getElementById('text_ed').value;
        } else {
            var text = document.getElementById('text_ed').value;
        }
        text = text.replace(/^[\s]*/g, '').replace(/[\s]*$/g, '').replace(/[\u0301\u0300]/g, '');

        $.post('inter_analyze', {
            text: text,
            cur_id: cur_id,
            private: settings[0],
            author_name: settings[1],
            text_name: settings[2],
            text_series: settings[3],
            text_year: settings[4],
            cons1: settings[5][0],
            cons2: settings[5][1],
            cons3: settings[5][2],
            comm1: settings[6][0],
            comm2: settings[6][1],
            ias1: settings[8][0],
            ias2: settings[8][1],
            ias3: settings[8][2],
            lang: settings[9]
        }).done(function (response) {
            trigger(response, settings[7]);
        }).fail(function () {
            console.log('fail');
        })
    }
}




function sort(event) {
    var classes = event.target.classList;

    parent = document.getElementById('all').childNodes[0].childNodes[0];
    child = document.getElementById('all').childNodes[0].childNodes[0].childNodes;
    if (document.getElementById('group_chain').checked) {
        if (!rep_group_list.length) {
            for (i = 1; i < child.length; i++) {
                number = child[i].childNodes[0].childNodes[0].innerText;
                ias = child[i].childNodes[2].innerText;
                chain = Math.ceil((child[i].childNodes[1].getElementsByTagName('SPAN').length) / 2);
                rep_group_list.push({ 'number': parseInt(number), 'chain': chain, 'ias': parseInt(ias), 'obj': child[i] })
            }
        }
        var list = rep_group_list.slice(0);
    } else if (!document.getElementById('group_chain').checked) {
        if (!rep_list.length) {
            for (i = 1; i < child.length; i++) {
                number = child[i].childNodes[0].childNodes[0].innerText;
                ias = child[i].childNodes[2].innerText;
                chain = Math.ceil((child[i].childNodes[1].getElementsByTagName('SPAN').length) / 2);
                rep_list.push({ 'number': parseInt(number), 'chain': chain, 'ias': parseInt(ias), 'obj': child[i] })
            }
        }
        var list = rep_list.slice(0);
    }
    switch (classes[1].substr(5)) {
        case 'number':
            list.sort((a, b) => (a.number > b.number) ? 1 : ((b.number > a.number) ? -1 : 0));
            break;
        case 'chain':
            list.sort((a, b) => (a.chain > b.chain) ? 1 : ((b.chain > a.chain) ? -1 : 0));
            break;
        case 'ias':
            list.sort((a, b) => (a.ias > b.ias) ? 1 : ((b.ias > a.ias) ? -1 : 0));
    }
    
    if (classes.contains('active-up')) {
        event.target.classList.remove('active-up');
        event.target.classList.add('active-down');
    } else if (classes.contains('active-down')) {
        list.reverse();
        event.target.classList.remove('active-down');
        event.target.classList.add('active-up');
    } else {
        while (document.getElementsByClassName('active-up').length) {
            document.getElementsByClassName('active-up')[0].classList.remove('active-up');
        }
        while (document.getElementsByClassName('active-down').length) {
            document.getElementsByClassName('active-down')[0].classList.remove('active-down');
        }
        if (classes[1].substr(5) == 'number') {
            event.target.classList.add('active-down');
        } else {
            list.reverse();
            event.target.classList.add('active-up');
        }
    }

    new_table = document.createElement('tbody');
    new_table.appendChild(document.getElementById('all').childNodes[0].childNodes[0].childNodes[0]);
    collapse = [];
    for (i = 0; i < list.length; i++) {
        if (list[i].obj.classList.contains('multi')) {
            new_table.appendChild(list[i].obj);
            chain = (list[i].obj.classList + '').match(/par-[0-9]+/gi)[0].substr(4);
            for (o = 0; o < list.length; o++) {
                if (list[o].obj.classList.contains('collapse')) {
                    if ((list[o].obj.classList + '').match(/multi-[0-9]+/gi)[0].substr(6) == chain) {
                        new_table.appendChild(list[o].obj);
                    }
                }
            }
        } else if (list[i].obj.classList.contains('collapse')) {
        } else {
            new_table.appendChild(list[i].obj);
        }
    }
    document.getElementById('all').childNodes[0].removeChild(document.getElementById('all').childNodes[0].childNodes[0]);
    document.getElementById('all').childNodes[0].appendChild(new_table);
}


// Вспомогательное

function loaded() {
    /* 
     * функция при загрузке страницы
     */
    var clear = 0;

    color_rules();
    while (document.getElementById('text_ed').value[document.getElementById('text_ed').value.length - 1] == '\n' || document.getElementById('text_ed').value[document.getElementById('text_ed').value.length - 1] == ' ') {
        document.getElementById('text_ed').value = document.getElementById('text_ed').value.substr(0, document.getElementById('text_ed').value.length - 1);
    }
    try {
        document.getElementById('text_ed').oninput = function () {
            if (clear) {
                clearTimeout(clear);
            }
            clear = setTimeout(function () {
                inter_analyze()
            }, 1000);
        };
        document.getElementById('noname_button').style.opacity = .33;
    } catch (e) { }

    try {
        inter_analyze(true);
    } catch (e) { }

    window.onbeforeunload = function (evt) {
        if (unsaved_data == 1) {
            var message = "Имеются несохранённые данные.";
            if (typeof evt == "undefined") {
                evt = window.event;
            }
            if (evt) {
                evt.returnValue = message;
            }
            return message;
        }
    }
}


/* глобальные данные */
var unsaved_data = 0,
    rep_list = [],
    rep_group_list = [],
    stat = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    need_stat = true;
/* --- */


window.onload = loaded;