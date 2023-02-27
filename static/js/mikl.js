styles_dict = [
    { 'type': 'background-color', 'set': 'rgba(0,255,70,0.5)', 'unset':'', 'used': -1 },
    { 'type': 'color', 'set': 'rgba(255,0,0,1)', 'unset':'', 'used': -1 },
    { 'type': 'color', 'set': 'rgba(255,0,0,1)', 'unset':'', 'used': -1 },
    { 'type': 'font-weight', 'set': '800', 'unset':'', 'used': -1 },
    { 'type': 'font-style', 'set': 'italic', 'unset':'', 'used': -1 },
    { 'type': 'text-decoration', 'set': 'underline', 'unset':'', 'used': -1 },
    { 'type': 'outline', 'set': 'dotted 2px #673ab7', 'unset':'', 'used': -1 },
    { 'type': 'background-image', 'set': 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAFCAYAAACEhIafAAAAF0lEQVQYV2NgYPjfwMDA8N+YARn8NwYANtMD5IC7yyQAAAAASUVORK5CYII=)', 'unset':'', 'used': -1 },

];
syll_dict = { 'type': 'border', 'set': 'solid 2px blue', 'unset':'', 'used': -1 }

styles_dict = [
    { 'type': '--ml0', 'set': '-127', 'unset':'', 'used': -1 },
    { 'type': '--ml1', 'set': '-127', 'unset':'', 'used': -1 },
    { 'type': '--ml2', 'set': '-127', 'unset':'', 'used': -1 },
    { 'type': 'font-weight', 'set': '800', 'unset':'', 'used': -1 },
    { 'type': 'font-style', 'set': 'italic', 'unset':'', 'used': -1 },
    { 'type': 'text-decoration', 'set': 'underline', 'unset':'', 'used': -1 },
    { 'type': 'outline', 'set': 'dotted 2px #673ab7', 'unset':'', 'used': -1 },
    { 'type': 'background-image', 'set': 'url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAFCAYAAACEhIafAAAAF0lEQVQYV2NgYPjfwMDA8N+YARn8NwYANtMD5IC7yyQAAAAASUVORK5CYII=)', 'unset':'', 'used': -1 },
];

syll_dict.styleTag = $('<style></style>');
$('html > head').append(syll_dict.styleTag);

function get_style(id){
    for (i = 0; i < styles_dict.length; i += 1){
        if (styles_dict[i].used == id){
            return styles_dict[i];
        }
    }
    return false;
};

function get_free_style(id){
    for (i = 0; i < styles_dict.length; i += 1){
        if (styles_dict[i].used == -1){
            styles_dict[i].used = id;
            if (!styles_dict[i].styleTag){
                styles_dict[i].styleTag = $('<style></style>');
                $('html > head').append(styles_dict[i].styleTag);
            }
            return styles_dict[i];
        }
    }
    return false;
};

function free_style(id){
    for (i = 0; i < styles_dict.length; i += 1){
        if (styles_dict[i].used == id){
            styles_dict[i].used = -1;
            return true;
        }
    }
    return false;
};

function h_show(e, tmp_style){
    $('.colorbtn').css('background-image', 'none');
    e = e.parentNode.parentNode;
    var cur = $(e);
    var id = cur.parent()[0].id
    tmp = cur.parent().find('.allrep>span>span');
    base = ', #txt > .';
    res = '#' + id + '>div>.btn';
    for (i = 0; i < tmp.length; i+=1){
        if ($('.'+tmp[i].className)[0].innerHTML == "\u200B"){
            res += base + 'l' + (tmp[i].className.substring(1) - 0 + 1);
        }
        else{
            res += base + tmp[i].className;
        }
    }

    if (cur.hasClass("shw")){
        $('.img'+id).css('display','none');
        cur.removeClass("shw");
        var tmp_style = get_style(id)
        tmp_style.styleTag.html('')
        free_style(id);
    }else{
        if (styles_dict[tmp_style].used != -1)
        {
            alert("Already used");
            return;
        }
        tmp_style = styles_dict[tmp_style]
        tmp_style.used = id;
        tmp_style.styleTag = $('<style></style>');
        tmp_style.styleTag.html(res + '{' + tmp_style.type+':' + tmp_style.set + '}');
        $('html > head').append(tmp_style.styleTag);
        cur.addClass("shw");
    }
    tmp = cur.parent().find('.dropdown-menu');
    tmp.hide();
};


$(".highlight").click(function(e){
    var cur = $(e.currentTarget.parentNode);
    var id = cur[0].parentNode.id
    tmp = cur.find('.allrep>span>span');
    base = ', #txt > .';
    res = '#' + id + '>.highlight';
    for (i = 0; i < tmp.length; i+=1){
        if ($('.'+tmp[i].className)[0].innerHTML == "\u200B"){
            res += base + 'l' + (tmp[i].className.substring(1) - 0 + 1);
        }
        else{
            res += base + tmp[i].className;
        }
    }

    if (cur.hasClass("shw")){
        cur.removeClass("shw");
        var tmp_style = get_style(id)
        tmp_style.styleTag.html('')
        free_style(id);
    }else{
        tmp = cur.find('.dropdown-menu');
        tmp.show();
    }
});

$('.rep').click(function(e){
    var cur = $(e.currentTarget);
    var id = cur.parent().parent()[0].id
    tmp = cur.find('span');
    base1 = ', #' + id + '>.allrep>.rep>.';
    base2 = ', #txt>.'
    res = '.none';
    for (i = 0; i < tmp.length; i+=1){
        res += base1 + tmp[i].className + base2 + tmp[i].className;
    }

    if (cur.hasClass("show")){
        cur.removeClass("show");
        syll_dict.styleTag.html('')
    }else{
        cur.addClass("show");
        syll_dict.styleTag.html(res + '{' + syll_dict.type+':' + syll_dict.set + '}');
    };
});

$('.slider').slider({
    tooltip_position:'bottom',
});

function my_send()
{
    $('form').attr('target', '_self');
    $('form').attr('action',"?lng="+location.search.substr(5));
    $('form').submit();
};

function my_send_stat()
{
    $('form').attr('target', '_blank');
    $('form').attr('action',"./statistic?lng="+location.search.substr(5));
    $('form').submit();
};

function my_send_svg()
{
    $('form').attr('target', '_blank');
    $('form').attr('action',"./svg?lng="+location.search.substr(5));
    $('form').submit();
};

function get_CSS(e)
{
    cms = getComputedStyle(e);
//    return cms.cssText;
    return  'background-color:' + cms.backgroundColor +
            ';background-image:' + cms.backgroundImage +
            ';color:' + cms.color +
            ';font-weight:' + cms.fontWeight +
            ';font-style:' + cms.fontStyle +
            ';text-decoration:' + cms.textDecoration +
            ';outline:' + cms.outline;
}


function my_copy()
{
    a = document.createElement('div')
    document.body.append(a);
    res = '<span>';
    tmp = '';
    $('#txt').children('span').each(function(i,e){
        newstyle = get_CSS(e);
        if (newstyle==tmp){
            txt = e.innerHTML
            if (txt == "\n"){
                res += '</span><br/><span>';
                tmp = '';
            }else if(txt != "\u200B") {res += txt;}
        }else{
            res += '</span><span style="'+ newstyle +'">' + e.innerHTML;
            tmp = newstyle;
        }
    });
    res += '</span>'
    $(a).html(res);
    document.getSelection().selectAllChildren(a);
    document.execCommand('copy');
    a.remove();
}

$('#txt > span').mouseover(
    function(el){
        $('.' + el.target.className).css('opacity','0.5');
        $('span.' + el.target.className).each(function(i,seq){
            if (seq.parentNode.id != "text" ){
                $('#' + seq.parentNode.parentNode.id + ' > .rep > span').each(function(i,let){
                    $('.'+let.className).css('opacity','0.5')
                })
            }
        })
    }
).mouseout(
    function(el){
        $('.' + el.target.className).css('opacity','1');
        $('span.' + el.target.className).each(function(i,seq){
            if (seq.parentNode.id != "text" ){
                $('#' + seq.parentNode.parentNode.id + ' > .rep > span').each(function(i,let){
                    $('.'+let.className).css('opacity','1')
                })
            }
        })
    }
).click(
    function(el){
        el = $('.' + el.target.className)
        tmp = el.css('text-shadow')
        el.css('text-shadow', (tmp == 'none')?'0px 0px 3px rgba(255, 0, 0, 1)':'none');
    }
).select(
    function(el){
        // console.log(el);
    }
);
window.onkeydown = function(key){
    if (key.code == "BracketLeft"){ $('#text').css('font-size', $('#text').css('font-size').replace(/[^0-9]/g, '') - 0 + 1+ "px"); return};
    if (key.code == "BracketRight"){ $('#text').css('font-size', $('#text').css('font-size').replace(/[^0-9]/g, '') - 1 + "px"); return};
    if (key.code == "NumpadMultiply"){
        $('*[x]').each(function(i, e){
            e.setAttributeNS(null, "x", e.getAttributeNS(null, "x") * 2);
            if (e.width){
                e.setAttributeNS(null, "width", e.getAttributeNS(null, "width") * 2);
            }
        });
        $('path').each(function(i, e){
            ar = $(e).attr('d').split(' ');
            for (i=0; i<ar.length; i+=1){
                if (ar[i] == "M"){ar[i+1] *= 2;};
                if (ar[i] == "L"){ar[i+1] *= 2;};
            };
            $(e).attr('d', ar.join(' '));
        });
    }
    if (key.code == "NumpadDivide"){
        $('*[x]').each(function(i, e){
            e.setAttributeNS(null, "x", e.getAttributeNS(null, "x") / 2);
            if (e.width){
                e.setAttributeNS(null, "width", e.getAttributeNS(null, "width") / 2);
            }
        })
        $('path').each(function(i, e){
            ar = $(e).attr('d').split(' ');
            for (i=0; i<ar.length; i+=1){
                if (ar[i] == "M"){ar[i+1] /= 2;};
                if (ar[i] == "L"){ar[i+1] /= 2;};
            };
            $(e).attr('d', ar.join(' '));
        });

    }
}

function nextNode(node) {
    if (node.hasChildNodes()) {
        return node.firstChild;
    } else {
        while (node && !node.nextSibling) {
            node = node.parentNode;
        }
        if (!node) {
            return null;
        }
        return node.nextSibling;
    }
}

function getRangeSelectedNodes(range) {
    var node = range.startContainer;
    var endNode = range.endContainer;

    // Special case for a range that is contained within a single node
    if (node == endNode) {
        return [node];
    }

    // Iterate nodes until we hit the end container
    var rangeNodes = [];
    while (node && node != endNode) {
        rangeNodes.push( node = nextNode(node) );
    }

    // Add partially selected nodes at the start of the range
    node = range.startContainer;
    while (node && node != range.commonAncestorContainer) {
        rangeNodes.unshift(node);
        node = node.parentNode;
    }

    return rangeNodes;
}

function getSelectedNodes() {
    if (window.getSelection) {
        var sel = window.getSelection();
        if (!sel.isCollapsed) {
            return getRangeSelectedNodes(sel.getRangeAt(0));
        }
    }
    return [];
}

document.onselectionchange = function(){
    $('#txt>span').css('color', 'black').css('text-shadow','none');
    $('#repeats>div>span>span>span').css('color', 'black').css('text-shadow','none');
    getSelectedNodes().forEach(function(el){
        if (el.nodeName == "#text") {el = el.parentNode};
        if (el.parentNode.id != 'txt') return;
        $('span.' + el.classList[0]).css('color','red').css('text-shadow', '0 0 2px blue');
        $('span.' + el.classList[0]).each(function(i,seq){
            if (seq.parentNode.id != "txt" ){
                $('#' + seq.parentNode.parentNode.parentNode.id + ' > .allrep > .rep > span').each(function(i,let){
                    $('#txt >.'+let.className).css('color','red').css('text-shadow', '0 0 2px blue');
                })
            }
        })
    })
}

$("#filter").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#repeats>div.repeat_line").each(function(i, el) {
        // console.log(el,$(el).text().substr(40), $(el).text().toLowerCase().indexOf(value));
        if ($(el).text().substr(40).toLowerCase().indexOf(value) > -1){
            $(el).css('display','grid')
        }
    else{
        $(el).css('display','none')
    }
    });
});

$('.hslide').on('mousedown', function(e){
    document._p_w = $(e.target.previousElementSibling).width();
    document._p_x = e.clientX;
    document._p_p = 1;
    document._p_t = e.target
}).on('mouseup', function(e){
    document._p_p = 0;
    // console.log('out', e);
})
$(document).on('mousemove',function(e){
    if (document._p_p == 1){
        t = document._p_t
        $(t.previousElementSibling).width((document._p_w + e.clientX - document._p_x)+'px');
    }
})

$('#sort_sum').click(function(e){
    a = $('#repeats>div.repeat_line');
    e = e.target;
    if ($(e).val() == 'max'){
        $(e).parent().find('input.btn').val('□');
        a.sort(function(e,f){return $(e).find('.summ').html() - $(f).find('.summ').html();});
        $(e).val('min');
    }else{
        $(e).parent().find('input.btn').val('□');
        a.sort(function(e,f){return $(f).find('.summ').html() - $(e).find('.summ').html();});
        $(e).val('max');
    }
    a.each(function(i,e){e.style.order = i});
});

$('#sort_mean').click(function(e){
    a = $('#repeats>div.repeat_line');
    e = e.target;
    if ($(e).val() == 'max'){
        $(e).parent().find('input.btn').val('□');
        a.sort(function(e,f){return $(e).find('.mean').html() - $(f).find('.mean').html();});
        $(e).val('min');
    }else{
        $(e).parent().find('input.btn').val('□');
        a.sort(function(e,f){return $(f).find('.mean').html() - $(e).find('.mean').html();});
        $(e).val('max');
    }
    a.each(function(i,e){e.style.order = i});
});

$('#sort_cnt').click(function(e){
    a = $('#repeats>div.repeat_line');
    e = e.target;
    if ($(e).val() == 'max'){
        $(e).parent().find('input.btn').val('□');
        a.sort(function(e,f){return $(e).find('.count').html() - $(f).find('.count').html();});
        $(e).val('min');
    }else{
        $(e).parent().find('input.btn').val('□');
        a.sort(function(e,f){return $(f).find('.count').html() - $(e).find('.count').html();});
        $(e).val('max');
    }
    a.each(function(i,e){e.style.order = i});
});

$('#show_simple').click(function(e){
    if ($('.allrep').css('flex-wrap') != 'nowrap'){
        $('.allrep').css('flex-wrap', 'nowrap')
        $('#show_simple').text('⏎');
    }else{
        $('.allrep').css('flex-wrap', 'wrap');
        $('#show_simple').text('⇨');
    }
});

$('#axes_1>g>g>use').mouseenter(function(e){
    l = $(e.target).parent().find('use');
    a = $('#txt').find('span');
    maxn = a[a.length - 1].classList[1].substr(1) - 0;
    num = maxn * (e.target.x.baseVal.value - l[0].x.baseVal.value)/(l[l.length - 1].x.baseVal.value - l[0].x.baseVal.value)
    num = Math.round(num);
    s = $('.s' + (num-1));
    res = '';
    for(i = 1; i < s.length; i++){
        res += $(s[i]).text();
    };
    s = $('.s' + num);
    for(i = 0; i < s.length; i++){
        res += $(s[i]).text();
    };
    axis_y = $('#matplotlib\\.axis_2').find('text')
    pwr = axis_y[axis_y.length - 1].textContent * (e.target.getAttributeNS(null, 'y') - axis_y[0].getAttributeNS(null, 'y')) / (axis_y[axis_y.length - 1].getAttributeNS(null, 'y') - axis_y[0].getAttributeNS(null, 'y'))
    $($('#__TXT')[0]).text(res + '(' + pwr.toFixed(2) + ')');
    $('#__TXT')[0].setAttributeNS(null, "x", e.target.getAttributeNS(null, "x"));
    $('#__TXT')[0].setAttributeNS(null, "y", e.target.getAttributeNS(null, "y") - 10);
    e.target.style.opacity = 0.3;
})

$('#axes_1>g>g>use').mouseleave(function(e){
    e.target.style.opacity = 1;
})

$('#axes_2>g>g>use').mouseenter(function(e){
    l = $(e.target).parent().find('use');
    a = $('#txt').find('span');
    maxn = a[a.length - 1].classList[2].substr(1) - 0;
    num = maxn * (e.target.x.baseVal.value - l[0].x.baseVal.value)/(l[l.length - 1].x.baseVal.value - l[0].x.baseVal.value)
    num = Math.round(num);
    s = $('.w'+num);
    res = '';
    for(i = 0; i < s.length; i++){
        res += $(s[i]).text();
    };
    axis_y = $('#matplotlib\\.axis_4').find('text')
    pwr = axis_y[axis_y.length - 1].textContent * (e.target.getAttributeNS(null, 'y') - axis_y[0].getAttributeNS(null, 'y')) / (axis_y[axis_y.length - 1].getAttributeNS(null, 'y') - axis_y[0].getAttributeNS(null, 'y'))
    $($('#__TXT')[0]).text(num + ':' + res + '(' + pwr.toFixed(2) + ')');
    $('#__TXT')[0].setAttributeNS(null, "x", e.target.getAttributeNS(null, "x"));
    $('#__TXT')[0].setAttributeNS(null, "y", e.target.getAttributeNS(null, "y") - 10);
    e.target.style.opacity = 0.3;
})

$('#axes_2>g>g>use').mouseleave(function(e){
    e.target.style.opacity = 1;
    $('#__TXT')[0].setAttributeNS(null, "y", -1000);
})

var el = document.createElementNS("http://www.w3.org/2000/svg", "text");
el.setAttributeNS(null, "id", "__TXT");
el.setAttributeNS(null, "x", 0);
el.setAttributeNS(null, "y", 0);
el.setAttributeNS(null, "text-anchor", "middle");
el.setAttributeNS(null, "fill", "black");
el.setAttributeNS(null, "filter", "drop-shadow(0px 0px 1px rgb(0 0 255 / 1))");
$('svg>g').append(el)

jscolor.presets.default = {
    mode:'HSV',
};

panzoom($('svg>g')[0]);

function rgbToHsl(r, g, b){
    r /= 255, g /= 255, b /= 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h, s, l = (max + min) / 2;

    if(max == min){
        h = s = 0;
    }else{
        var d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch(max){
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h = Math.ceil(h * 60);
    }
    l = Math.ceil(l * 100)
    return [h, s, l];
}

function root_edit(color, i){
    var r = parseInt(color.toHEXAString().substr(1,2), 16);
    var g = parseInt(color.toHEXAString().substr(3,2), 16);
    var b = parseInt(color.toHEXAString().substr(5,2), 16);
    cl = rgbToHsl(r, g, b)
    document.documentElement.style.setProperty('--cl' + i + 'h', cl[0]);
    document.documentElement.style.setProperty('--cl' + i + 'l', cl[2] + '%');
    color.previewElement.style.backgroundImage = 'none';
}