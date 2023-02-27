var txt = document.location.pathname.substr(6,4);
if ((txt == 'edit') || (txt == 'text'))
{
    var script = document.createElement('script');
    script.src = 'http://syllabica.com/static/js/phonotext.text-edit.js?date=010219';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);

    var script = document.createElement('script');
    script.src = 'http://syllabica.com/static/js/phonotext.text-edit.accents.js?date=010219';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);

    var script = document.createElement('script');
    script.src = 'http://syllabica.com/static/js/phonotext.text-edit.colors.js?date=010219';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);
}
else
{
    var script = document.createElement('script');
    script.src = 'http://syllabica.com/static/js/phonotext.index-dict.js?date=010219';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);
}