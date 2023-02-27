'''
Выкачивание ударений с сайта https://где-ударение.рф/ и https://udaren.ru/
'''
import re
import asyncio
import aiohttp

async def get_online_gd(text, res):
    text = re.split(r'\b', text.lower())
    print(text)
    async with aiohttp.ClientSession() as session:
        for i in range(len(text)):
            async with session.get('https://где-ударение.рф/в-слове-'+text[i]) as resp:
                html = await resp.text()
                match = re.search(r'<div class="rule">([^<]*)— (?P<start>[^<]*)<b>(?P<letter>.)</b>(?P<end>[а-я]*)', html)
                if match is not None:
                    res_d = match.groupdict()
                    text[i] = res_d['start'] + res_d['letter'].lower() + '\U00000301' + res_d['end']
                await asyncio.sleep(0.05)

    res.append(''.join(text))

async def get_online(text, res):
    text = re.split(r'\b', text)
    print(text)
    async with aiohttp.ClientSession() as session:
        for i in range(len(text)):
            async with session.get('https://udaren.ru/'+text[i]) as resp:
                html = await resp.text()
                match = re.search(r'<span style="font-size: 40px;">([^<]*)<', html)
                if match is not None:
                    text[i] = match.groups()[0]

    res.append(''.join(text))

def get_accents(text):
    res = []
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_online_gd(text, res))
    return res[0]


if __name__ =="__main__":
    print(get_accents('''— Скажи-ка, дядя, ведь не даром
Москва, спаленная пожаром,
Французу отдана?
Ведь были ж схватки боевые,
Да, говорят, еще какие!
Недаром помнит вся Россия
Про день Бородина!'''))