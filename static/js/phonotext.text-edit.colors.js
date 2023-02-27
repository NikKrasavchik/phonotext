// глобальный контейнер для цветов, используемых при выделении фоносиллабов в основном тексте
var color_dict = [];


// Функции цветового выделения

function color_rules() {
    /*
     * добавление правил цветового выделения для обновлённых элементов
     */

    var underline = document.getElementsByClassName('underline'),   // элементы, принадлежащие к (>1) выделенной цепочке в основном тексте
        double = document.getElementsByClassName('rep-hyp'),        // элементы отвечающие за 2 ФС (в цепочках повторов разделители и ФС со скобками)
        ps_elem = [                                                 // элементы отвечающие за выделение потенциального слога
            document.getElementsByClassName('base'),    // элементы основного текста (центральный блок)
            document.getElementsByClassName('syll'),    // элементы вкладки "sp(max)"
        ],
        fs_elem = [                                                 // элементы отвечающие за выделение фоносиллаба
            document.getElementsByClassName('rep'),     // элементы вкладки "повторы"
            document.getElementsByClassName('comb')     // элементы вкладки "фоносиллабы"
        ],
        chain = document.getElementsByClassName('btn-underline'),
        test = 0;

    //удаляем лишние триггеры с base
    copy = Array.from(ps_elem[0]);
    for (i = ps_elem[0].length - 1; i >= 0; i--) {
        if (ps_elem[0][i].classList.contains('base--1')) {
            copy.splice(i, 1);
        }
    }
    ps_elem[0] = copy;

    // проверка наличия какого-либо цветового выделения, для изменения отображения кнопки "очистить"
    for (i = 0; i < color_dict.length; i++) {
        if (color_dict[i].used != -1) {
            test = 1;
            break;
        }
    }
    if (test) {
        document.getElementById('highlight_button').disabled = false;
        document.getElementById('highlight_button').style.opacity = 1;
    } else {
        document.getElementById('highlight_button').disabled = true;
        document.getElementById('highlight_button').style.opacity = .5;
    }

    // вызов ps_event() при движении по элементам ps_elem
    for (o = 0; o < ps_elem.length; o++) {
        for (i = 0; i < ps_elem[o].length; i++) {
            ps_elem[o][i].onmouseover = ps_elem[o][i].onmouseout = ps_event;
        }
    }

    // вызов fs_event() при движении по элементам fs_elem
    for (o = 0; o < fs_elem.length; o++) {
        for (i = 0; i < fs_elem[o].length; i++) {
            fs_elem[o][i].onmouseover = fs_elem[o][i].onmouseout = fs_event;
        }
    }

    // вызов chain_event() при движении и клике по элементам chain
    for (i = 0; i < chain.length; i++) {
        chain[i].onmouseover = chain[i].onmouseout = chain[i].onclick = chain_event;
    }

    // вызов double_event() при движении по элементам double
    for (i = 0; i < double.length; i++) {
        double[i].onmouseover = double[i].onmouseout = double_event;
    }

    // вызов under_event() при клике по элементам underline
    for (i = 0; i < underline.length; i++) {
        underline[i].onclick = under_event;
        underline[i].onmouseover = underline[i].onmouseout = null;
    }
}


function ps_event(event) {
    /* 
     * событие выделения потенциального слога при движении по элементам "base" и "syll"
     */
    
    var main_elem = document.getElementsByClassName('base base-' + event.target.classList[1].substr(5))[0],
        prev = main_elem.previousSibling,
        next = main_elem.nextSibling;


    main_elem.classList.toggle('color-active');

    while (prev && prev.tagName == 'SPAN' && prev.classList.contains('base--1')) {
        prev.classList.toggle('color-active');
        prev = prev.previousSibling;
    }
    while (prev && prev.nextSibling.innerText.match(/[^а-яёa-z]/i) != null) {
        prev.nextSibling.classList.toggle('color-active');
        prev = prev.nextSibling;
    }

    while (next && next.tagName == 'SPAN' && next.classList.contains('base--1')) {
        next.classList.toggle('color-active');
        next = next.nextSibling;
    }
    while (next && next.previousSibling.innerText.match(/[^а-яёa-z]/i) != null) {
        next.previousSibling.classList.toggle('color-active');
        next = next.previousSibling;
    }

}


function fs_event(event, target, setter) {
    /* 
     * событие выделения фоносиллаба при движении по элементам "rep" и "comb"
     */

    // проверяем, вызвано событие напрямую, или с функции цепи
    if (event != null) {
        target = event.target;
    }

    // определение основной гласной потенциального слога и её соседей, а также позиции гласной в фоносиллабе
    var main_elem = document.getElementsByClassName('base base-' + target.classList[1].substr(5))[0],
        inner = target.innerText.replace(/[()]/g, ''),
        prev = main_elem.previousSibling,
        next = main_elem.nextSibling,
        vow = inner.search(/[ёеуэоаыяиюiaeou]/),
        dift = (inner.match(/au|ea|ee|eu|ie|oa|ou|oe|ai/g) || []).length;
        prev_arr = [],
        next_arr = [];
    
    while (prev.innerText == '') {
        prev = prev.previousSibling;
    }

    if (prev.innerText.search(/[ьъ]/) != -1) {
        prev = prev.nextSibling;
    }

    // определение массива выделения предыдущих элементов
    for (i = 0; i < vow; i++) {
        if (inner[i].match(/[-|]/)) {
            prev_arr.unshift(0);
        } else {
            prev_arr.unshift(1);
        }
    }

    // определение массива выделения следующих элементов
    for (i = inner.length - 1; i > vow; i--) {
        if (inner[i].match(/[-|]/)) {
            next_arr.unshift(0);
        } else {
            next_arr.unshift(1);
        }
    }

    if (dift != 0) {
        next_arr.shift();
    }
    

    main_elem.classList.toggle('color-active', setter);

    for (i = 0; i < prev_arr.length; i++) {
        while (1) {
            if (prev.innerText.match(/[^а-щыэюяё a-z]/i) != null) {
                prev = prev.previousSibling;
                continue;
            }
            if (prev.nextSibling && (prev.innerText + prev.nextSibling.innerText).match(/ll|mm|nn|rr|ck|e[^a-zа-я]|([а-я])\1/i) != null) {
                prev = prev.previousSibling;
                continue;
            }
            if (prev.previousSibling && (prev.previousSibling.innerText + prev.innerText).match(/[gtckprw]h/i) != null) {
                prev = prev.previousSibling;
                continue;
            }
            if (prev.nextSibling && prev.nextSibling.nextSibling && (prev.innerText + prev.nextSibling.innerText
                + prev.nextSibling.nextSibling.innerText).match(/e[sd][^a-zа-я]|sc[iey]/i) != null) {
                prev = prev.previousSibling;
                continue;
            }
            break;
        }
        if ((prev.innerText.match(/x/i) != null)
            || (prev.nextSibling && prev.nextSibling.nextSibling && (prev.innerText + prev.nextSibling.innerText + prev.nextSibling.nextSibling.innerText).match(/ci[ieaou]/i) != null)
            || (prev.previousSibling && prev.nextSibling && prev.nextSibling.nextSibling &&
                (prev.previousSibling.innerText + prev.innerText + prev.nextSibling.innerText + prev.nextSibling.nextSibling.innerText).match(/[a-z][st]i[ieaou]/i) != null)) {
            if ((prev_arr[i] || prev_arr[i+1]) && prev.innerText != ' ') {
                prev.classList.toggle('color-active', setter);
            }
            prev_arr.splice(i, 1);
        } else if (prev_arr[i] && prev.innerText != ' ') {
            prev.classList.toggle('color-active', setter);
        }
        prev = prev.previousSibling;
    }

    for (i = 0; i < next_arr.length; i++) {
        while (1) {
            if (next.innerText.match(/[^а-щыэюяё a-z]/i) != null) {
                next = next.nextSibling;
                continue;
            }
            if (next.nextSibling && (next.innerText + next.nextSibling.innerText).match(/e[^a-zа-я]/i) != null) {
                next = next.nextSibling;
                continue;
            }
            if (next.previousSibling && (next.previousSibling.innerText + next.innerText).match(/[gtckprw]h|ll|mm|nn|rr|ck|([а-я])\1/i) != null) {
                next = next.nextSibling;
                continue;
            }
            if (next.nextSibling && next.nextSibling.nextSibling && (next.innerText + next.nextSibling.innerText
                + next.nextSibling.nextSibling.innerText).match(/e[sd][^a-zа-я]|sc[iey]/i) != null) {
                next = next.nextSibling;
                continue;
            }
            break;
        }
        if (dift > 1 && next.innerText.match(/au|ea|ee|eu|ie|oa|ou|oe|ai/i) != null) {
            i++;
        }
        if ((next.innerText.match(/x/i) != null)
            || (next.nextSibling && next.nextSibling.nextSibling && (next.innerText + next.nextSibling.innerText + next.nextSibling.nextSibling.innerText).match(/ci[ieaou]/i) != null)
            || (next.previousSibling && next.nextSibling && next.nextSibling.nextSibling &&
                (next.previousSibling.innerText + next.innerText + next.nextSibling.innerText + next.nextSibling.nextSibling.innerText).match(/[a-z][st]i[ieaou]/i) != null)) {
            if ((next_arr[i] || next_arr[i + 1]) && next.innerText != ' ') {
                next.classList.toggle('color-active', setter);
            }
            next_arr.splice(i, 1);
        } else if (next_arr[i] && next.innerText != ' ') {
            next.classList.toggle('color-active', setter);
        }
        next = next.nextSibling;
    }
}


function double_event(event) {
    /*
     * событие движения по элементам с двойной принадлежностью
     */

    if (event.type == 'mouseover') {
        var setter = true;
    } else if (event.type == 'mouseout') {
        var setter = false;
    }
    // если элемент – фоносиллаб с двойной принадлежностью, то так и передаём
    if (event.target.classList.contains('double')) {
        fs_event(null, event.target, setter);

    // если элемент – разделитель между фоносиллабами, то передаём соседей
    } else {
        var prev_item = event.target.previousSibling,
            next_item = event.target.nextSibling;

        // соседей собираем переступая через пустые "#text"
        while (prev_item.tagName != 'SPAN') {
            prev_item = prev_item.previousSibling;
        }
        while (next_item.tagName != 'SPAN') {
            next_item = next_item.nextSibling;
        }
        
        fs_event(null, prev_item, setter);
        fs_event(null, next_item, setter);
    }
}


function chain_event(event) {
    /*
     * событие движения/клика по кнопкам-"цепям"
     */

    // определяем базовые значения функции
    var elem_id = event.target.parentNode.parentNode.childNodes[1].getElementsByTagName('SPAN'),
        chain = event.target.innerText;

    // убираем разделители между фоносиллабами 
    copy = Array.from(elem_id);
    for (i = elem_id.length - 1; i >= 0; i--) {
        if (elem_id[i].classList.contains('rep-hyp') && !elem_id[i].classList.contains('double')) {
            copy.splice(i, 1);
        }
    }
    elem_id = copy;
    
    if (event.type == 'mouseover') {
        for (o = 0; o < elem_id.length; o++) {
            fs_event(null, elem_id[o], true);
        }
    } else if (event.type == 'mouseout') {
        for (o = 0; o < elem_id.length; o++) {
            fs_event(null, elem_id[o], false);
        }
    } else if (event.type == 'click') {
        if (event.target.classList.contains('active')) {
            event.target.classList.remove('active');
            for (o = 0; o < elem_id.length; o++) {
                var main_elem = document.getElementsByClassName('base base-' + elem_id[o].classList[1].substr(5))[0],
                    inner = elem_id[o].innerText.replace(/[()]/g, ''),
                    prev = main_elem.previousSibling,
                    next = main_elem.nextSibling,
                    vow = inner.search(/[ёеуэоаыяиюiaeou]/),
                    dift = (inner.match(/au|ea|ee|eu|ie|oa|ou|oe|ai/g) || []).length;
                    prev_arr = [],
                    next_arr = [];

                // определение массива выделения предыдущих элементов
                for (i = 0; i < vow; i++) {
                    if (inner[i].match(/[-|]/)) {
                        prev_arr.unshift(0);
                    } else {
                        prev_arr.unshift(1);
                    }
                }

                // определение массива выделения следующих элементов
                for (i = inner.length - 1; i > vow; i--) {
                    if (inner[i].match(/[-|]/)) {
                        next_arr.unshift(0);
                    } else {
                        next_arr.unshift(1);
                    }
                }

                function del_chain(elem) {
                    if (elem.classList.contains('active-' + chain)) {
                        elem.classList.remove('active-' + chain);
                    }
                    elem.classList.remove('chain-' + chain);
                    var count = elem.classList.value.match(/chain-[0-9]+/g);
                    if (count) {
                        if (count.length == 1) {
                            elem.classList.toggle('underline', false);
                            elem.classList.toggle('underline-dis', false);
                        }
                        var new_active = count[count.length - 1].slice(6);
                        elem.classList.add('active-' + new_active);
                        if (color_dict.filter(c => c.used == new_active).length != 0) {
                            new_color = color_dict.filter(c => c.used == new_active)[0].color;
                            elem.classList.add('color-' + new_color);
                        }
                    }
                    var old_color = color_dict.filter(c => c.used == chain)[0].color;
                    elem.classList.toggle('color-' + old_color, false);
                }

                if (dift != 0) {
                    next_arr.shift();
                }


                del_chain(main_elem);

                for (i = 0; i < prev_arr.length; i++) {
                    while (1) {
                        if (prev.innerText.match(/[^а-щыэюяё a-z]/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        if (prev.nextSibling && (prev.innerText + prev.nextSibling.innerText).match(/ll|mm|nn|rr|ck|e[^a-zа-я]|([а-я])\1/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        if (prev.previousSibling && (prev.previousSibling.innerText + prev.innerText).match(/[gtckprw]h/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        if (prev.nextSibling && prev.nextSibling.nextSibling && (prev.innerText + prev.nextSibling.innerText
                            + prev.nextSibling.nextSibling.innerText).match(/e[sd][^a-zа-я]|sc[iey]/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        break;
                    }
                    if ((prev.innerText.match(/x/i) != null)
                        || (prev.nextSibling && prev.nextSibling.nextSibling && (prev.innerText + prev.nextSibling.innerText + prev.nextSibling.nextSibling.innerText).match(/ci[ieaou]/i) != null)
                        || (prev.previousSibling && prev.nextSibling && prev.nextSibling.nextSibling &&
                            (prev.previousSibling.innerText + prev.innerText + prev.nextSibling.innerText + prev.nextSibling.nextSibling.innerText).match(/[a-z][st]i[ieaou]/i) != null)) {
                        if ((prev_arr[i] || prev_arr[i + 1]) && prev.innerText != ' ') {
                            del_chain(prev)
                        }
                        prev_arr.splice(i, 1);
                    } else if (prev_arr[i] && prev.innerText != ' ') {
                        del_chain(prev)
                    }
                    prev = prev.previousSibling;
                }

                for (i = 0; i < next_arr.length; i++) {
                    while (1) {
                        if (next.innerText.match(/[^а-щыэюяё a-z]/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        if (next.nextSibling && (next.innerText + next.nextSibling.innerText).match(/e[^a-zа-я]/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        if (next.previousSibling && (next.previousSibling.innerText + next.innerText).match(/[gtckprw]h|ll|mm|nn|rr|ck|([а-я])\1/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        if (next.nextSibling && next.nextSibling.nextSibling && (next.innerText + next.nextSibling.innerText
                            + next.nextSibling.nextSibling.innerText).match(/e[sd][^a-zа-я]|sc[iey]/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        break;
                    }
                    if (dift > 1 && next.innerText.match(/au|ea|ee|eu|ie|oa|ou|oe|ai/i) != null) {
                        i++;
                    }
                    if ((next.innerText.match(/x/i) != null)
                        || (next.nextSibling && next.nextSibling.nextSibling && (next.innerText + next.nextSibling.innerText + next.nextSibling.nextSibling.innerText).match(/ci[ieaou]/i) != null)
                        || (next.previousSibling && next.nextSibling && next.nextSibling.nextSibling &&
                            (next.previousSibling.innerText + next.innerText + next.nextSibling.innerText + next.nextSibling.nextSibling.innerText).match(/[a-z][st]i[ieaou]/i) != null)) {
                        if ((next_arr[i] || next_arr[i + 1]) && next.innerText != ' ') {
                            del_chain(next);
                        }
                        next_arr.splice(i, 1);
                    } else if (next_arr[i] && next.innerText != ' ') {
                        del_chain(next);
                    }
                    next = next.nextSibling;
                }
            }
            color_dict.filter(c => c.used == chain)[0].used = -1;

        } else {
            var unused_colors = color_dict.filter(c => c.used == -1);
            if (unused_colors[0]) {
                var current_color = unused_colors[0].color;
                unused_colors[0].used = chain;
            } else {
                var current_color = color_dict.length + 1;
                color_dict.push({ 'color': color_dict.length + 1, 'used': chain })
            }
            event.target.classList.add('active');
            for (o = 0; o < elem_id.length; o++) {
                var main_elem = document.getElementsByClassName('base base-' + elem_id[o].classList[1].substr(5))[0],
                    inner = elem_id[o].innerText.replace(/[()]/g, ''),
                    prev = main_elem.previousSibling,
                    next = main_elem.nextSibling,
                    vow = inner.search(/[ёеуэоаыяиюiaeou]/),
                    dift = (inner.match(/au|ea|ee|eu|ie|oa|ou|oe|ai/g) || []).length;
                    prev_arr = [],
                    next_arr = [];

                // определение массива выделения предыдущих элементов
                for (i = 0; i < vow; i++) {
                    if (inner[i].match(/[-|]/)) {
                        prev_arr.unshift(0);
                    } else {
                        prev_arr.unshift(1);
                    }
                }

                // определение массива выделения следующих элементов
                for (i = inner.length - 1; i > vow; i--) {
                    if (inner[i].match(/[-|]/)) {
                        next_arr.unshift(0);
                    } else {
                        next_arr.unshift(1);
                    }
                }

                function add_chain(elem) {
                    if (elem.classList.value.match(/active-[0-9]+/)) {
                        elem.classList.remove(elem.classList.value.match(/active-[0-9]+/));
                        if (!elem.classList.contains('underline') && !elem.classList.contains('underline-dis')) {
                            if (elem.classList.contains('base--1')) {
                                elem.classList.add('underline-dis');
                            } else {
                                elem.classList.add('underline');
                            }
                        }
                    }
                    if (elem.classList.value.match(/color-[0-9]+/)) {
                        elem.classList.toggle(elem.classList.value.match(/color-[0-9]+/)[0], false);
                    }
                    elem.classList.add('color-' + current_color);
                    elem.classList.add('chain-' + chain);
                    elem.classList.add('active-' + chain);
                }

                if (dift != 0) {
                    next_arr.shift();
                }


                add_chain(main_elem);

                for (i = 0; i < prev_arr.length; i++) {
                    while (1) {
                        if (prev.innerText.match(/[^а-щыэюяё a-z]/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        if (prev.nextSibling && (prev.innerText + prev.nextSibling.innerText).match(/ll|mm|nn|rr|ck|e[^a-zа-я]|([а-я])\1/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        if (prev.previousSibling && (prev.previousSibling.innerText + prev.innerText).match(/[gtckprw]h/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        if (prev.nextSibling && prev.nextSibling.nextSibling && (prev.innerText + prev.nextSibling.innerText
                            + prev.nextSibling.nextSibling.innerText).match(/e[sd][^a-zа-я]|sc[iey]/i) != null) {
                            prev = prev.previousSibling;
                            continue;
                        }
                        break;
                    }
                    if ((prev.innerText.match(/x/i) != null)
                        || (prev.nextSibling && prev.nextSibling.nextSibling && (prev.innerText + prev.nextSibling.innerText + prev.nextSibling.nextSibling.innerText).match(/ci[ieaou]/i) != null)
                        || (prev.previousSibling && prev.nextSibling && prev.nextSibling.nextSibling &&
                            (prev.previousSibling.innerText + prev.innerText + prev.nextSibling.innerText + prev.nextSibling.nextSibling.innerText).match(/[a-z][st]i[ieaou]/i) != null)) {
                        if ((prev_arr[i] || prev_arr[i + 1]) && prev.innerText != ' ') {
                            add_chain(prev)
                        }
                        prev_arr.splice(i, 1);
                    } else if (prev_arr[i] && prev.innerText != ' ') {
                        add_chain(prev)
                    }
                    prev = prev.previousSibling;
                }

                for (i = 0; i < next_arr.length; i++) {
                    while (1) {
                        if (next.innerText.match(/[^а-щыэюяё a-z]/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        if (next.nextSibling && (next.innerText + next.nextSibling.innerText).match(/e[^a-zа-я]/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        if (next.previousSibling && (next.previousSibling.innerText + next.innerText).match(/[gtckprw]h|ll|mm|nn|rr|ck|([а-я])\1/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        if (next.nextSibling && next.nextSibling.nextSibling && (next.innerText + next.nextSibling.innerText
                            + next.nextSibling.nextSibling.innerText).match(/e[sd][^a-zа-я]|sc[iey]/i) != null) {
                            next = next.nextSibling;
                            continue;
                        }
                        break;
                    }
                    if (dift > 1 && next.innerText.match(/au|ea|ee|eu|ie|oa|ou|oe|ai/i) != null) {
                        i++;
                    }
                    if ((next.innerText.match(/x/i) != null)
                        || (next.nextSibling && next.nextSibling.nextSibling && (next.innerText + next.nextSibling.innerText + next.nextSibling.nextSibling.innerText).match(/ci[ieaou]/i) != null)
                        || (next.previousSibling && next.nextSibling && next.nextSibling.nextSibling &&
                            (next.previousSibling.innerText + next.innerText + next.nextSibling.innerText + next.nextSibling.nextSibling.innerText).match(/[a-z][st]i[ieaou]/i) != null)) {
                        if ((next_arr[i] || next_arr[i + 1]) && next.innerText != ' ') {
                            add_chain(next);
                        }
                        next_arr.splice(i, 1);
                    } else if (next_arr[i] && next.innerText != ' ') {
                        add_chain(next);
                    }
                    next = next.nextSibling;
                }
            }
        }
        color_rules();
    }
}


function under_event(event) {
    var elem_id = event.target.classList[1].slice(5),
        active_id = event.target.classList.value.match(/active-[0-9]+/)[0].slice(7),
        buttons = document.getElementsByClassName('btn btn-sm btn-outline-secondary btn-underline active');
    for (i = 0; i < buttons.length; i++) {
        if (buttons[i].innerText == active_id) {
            active_chain = buttons[i];
            break;
        }
    }
    // определение основной гласной потенциального слога и её соседей, а также позиции гласной в фоносиллабе
    var elem_fs = active_chain.parentNode.parentNode.childNodes[1].getElementsByClassName('base-' + elem_id)[0],
        main_elem = document.getElementsByClassName('base base-' + elem_fs.classList[1].substr(5))[0];
    if (elem_fs.classList.contains('double')) {
        var base = elem_fs.classList.value.match(/base-[0-9]+/g);
        if (elem_id == base[1].substr(5)) {
            main_elem = document.getElementsByClassName('base base-' + elem_fs.classList[2].substr(5))[0];
        }
    }

    var inner = elem_fs.innerText.replace(/[()]/g, ''),
        prev = main_elem.previousSibling,
        next = main_elem.nextSibling,
        vow = inner.search(/[ёеуэоаыяию]/),
        prev_arr = [],
        next_arr = [];

    // определение массива выделения предыдущих элементов
    for (i = 0; i < vow; i++) {
        if (inner[i].match(/[-|]/)) {
            prev_arr.unshift(0);
        } else {
            prev_arr.unshift(1);
        }
    }

    // определение массива выделения следующих элементов
    for (i = inner.length - 1; i > vow; i--) {
        if (inner[i].match(/[-|]/)) {
            next_arr.unshift(0);
        } else {
            next_arr.unshift(1);
        }
    }
    
    var chain_list = main_elem.classList.value.match(/chain-[0-9]+/g),
        cur_active = main_elem.classList.value.match(/active-[0-9]+/)[0];
    if (chain_list.indexOf('chain-' + cur_active.substr(7)) == (chain_list.length - 1)) {
        new_active = chain_list[0].substr(6);
        new_color = color_dict.filter(c => c.used == chain_list[0].substr(6))[0].color;
    } else {
        for (o = 0; o < chain_list.length; o++) {
            if (chain_list.indexOf(chain_list[o]) > chain_list.indexOf('chain-' + cur_active.substr(7))) {
                new_active = chain_list[o].substr(6);
                new_color = color_dict.filter(c => c.used == chain_list[o].substr(6))[0].color;
                break;
            }
        }
    }
    main_elem.classList.remove(cur_active);
    main_elem.classList.remove(main_elem.classList.value.match(/color-[0-9]+/)[0]);
    main_elem.classList.add('active-' + new_active);
    main_elem.classList.add('color-' + new_color);

    for (i = 0; i < prev_arr.length; i++) {
        while (prev.innerText.match(/[^а-щыэюяяa-zё ]/i) != null) {
            prev = prev.previousSibling;
        }
        if (prev_arr[i]) {
            prev.classList.toggle(prev.classList.value.match(/active-[0-9]+/)[0], false);
            prev.classList.toggle(prev.classList.value.match(/color-[0-9]+/)[0], false);
            prev.classList.toggle('active-' + new_active, true);
            prev.classList.toggle('color-' + new_color, true);
        }
        prev = prev.previousSibling;
    }

    for (i = 0; i < next_arr.length; i++) {
        while (next.innerText.match(/[^а-щыэюяяa-zё ]/i) != null) {
            next = next.nextSibling;
        }
        if (next_arr[i]) {
            next.classList.toggle(next.classList.value.match(/active-[0-9]+/)[0], false);
            next.classList.toggle(next.classList.value.match(/color-[0-9]+/)[0], false);
            next.classList.toggle('active-' + new_active, true);
            next.classList.toggle('color-' + new_color, true);
        }
        next = next.nextSibling;
    }
}


function clear_highlight() {
    var child = document.getElementById('inter_text').childNodes;
    for (i = 0; i < child.length; i++) {
        child[i].classList = child[i].classList[0] + ' ' + child[i].classList[1];
    }
    while (document.getElementsByClassName('btn-underline active').length) {
        document.getElementsByClassName('btn-underline active')[0].classList.remove('active');
    }
    color_dict = [];
    document.getElementById('highlight_button').disabled = true;
    document.getElementById('highlight_button').style.opacity = .5;
}


function ias_map(id) {
    var child = document.getElementById('inter_text').childNodes,
        last = 0.4,
        arr = ['ias1', 'ias2', 'iasf', 'chains', null],
        step = 4,
        but_1 = document.getElementById('ias1').parentNode,
        but_2 = document.getElementById('ias2').parentNode,
        but_3 = document.getElementById('ias3').parentNode,
        but_4 = document.getElementById('chains').parentNode;
    if (id != 0 && but_1.classList.contains('active')) but_1.click();
    if (id != 1 && but_2.classList.contains('active')) but_2.click();
    if (id != 2 && but_3.classList.contains('active')) but_3.click();
    if (id != 3 && but_4.classList.contains('active')) but_4.click();
    if (id == 3) step = 2;
    if (but_4.classList.contains('active') || but_3.classList.contains('active') || but_2.classList.contains('active') || but_1.classList.contains('active')) {
        for (i = 0; i < child.length; i++) {
            child[i].style = '';
        }
    } else {
        for (i = 0; i < child.length; i++) {
            if (child[i].getAttribute(arr[id]) != null && child[i].getAttribute(arr[id]) != 'NaN') {
                new_last = (child[i].getAttribute(arr[id]) / 10);
                child[i].style = 'background: linear-gradient(to right, rgba(222,88,33,' + last ** step + '), rgba(222,88,33,' + new_last ** step + '));';
                last = new_last;
            } else {
                count = 0;
                while (child[i + count] && (child[i + count].getAttribute(arr[id]) == null || child[i + count].getAttribute(arr[id]) == 'NaN')) {
                    count++;
                }
                try {
                    diff = (((child[i + count].getAttribute(arr[id]) / 10) - last) / count);
                    for (o = 0; o < count; o++) {
                        if ((((last + (diff * o)) ** step) > 0.4) || (child[i + o].innerText.match(/[а-яё a-z]/i))) {
                            child[i + o].style = 'background: linear-gradient(to right, rgba(222,88,33,' + ((last + (diff * o)) ** step) + '), rgba(222,88,33,' + ((last + (diff * (o + 1))) ** step) + '));';
                        }
                    }
                    last = (child[i + count].getAttribute(arr[id]) / 10);
                } catch {
                    diff = ((0.4 - last) / count);
                    for (o = 0; o < count; o++) {
                        if ((((last + (diff * o)) ** step) > 0.4) || (child[i + o].innerText.match(/[а-яё a-z]/i))) {
                            child[i + o].style = 'background: linear-gradient(to right, rgba(222,88,33,' + ((last + (diff * o)) ** step) + '), rgba(222,88,33,' + ((last + (diff * (o + 1))) ** step) + '));';
                        }
                    }
                    last = 0.4;
                }
                i--;
                i += count;
            }
        }
    }
}