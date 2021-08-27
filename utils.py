import logging

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import random

from pylivestream import FileIn
from pylivestream.ffmpeg import Ffmpeg
from pylivestream.glob import fileglob
from pylivestream.utils import meta_caption
from tinytag import TinyTag

from serializers import Config, Extension

logging.basicConfig(filename='output.log', level=logging.INFO)


class Fake:

    @staticmethod
    def draw_text(text: str = None, up=False, row=1) -> list:
        # fontfile=/path/to/font.ttf:
        if not text:
            return []

        if up:
            part = '1/8'
            fontcolor = "fontcolor=yellow"
        else:
            part = '3/4'
            fontcolor = "fontcolor=white"
        fontsize = "fontsize=32"
        box = "box=1"
        boxcolor = "boxcolor=black@0.5"
        border = "boxborderw=5"
        x = "x=(w-text_w)/2"
        # y = f"y=h*{part}+(text_h+20)*{row}"
        y = f"y=h*{part}+40*{row}"
        # y = "y=(h-text_h)*3/4"

        return [
            "-vf",
            f"drawtext=text='{text}':{fontcolor}:{fontsize}:{box}:{boxcolor}:{border}:{x}:{y}",
        ]

    def draw_pray(self, text: str = None):
        if not text:
            return []

        text_list = text.split('|')
        meta = Fake.draw_text(text_list[0])

        if len(text_list) == 1:
            return meta

        result = meta

        pray_rows = insert_line_breaks(text_list[1]).split('\n')

        for row, string in enumerate(pray_rows, 1):
            cmd_list = Fake.draw_text(string, up=True, row=row)
            if not cmd_list:
                continue
            if not result:
                result = cmd_list
            else:
                result[1] += f', {cmd_list[1]}'

        return result


def insert_line_breaks(text: str):
    result = ''
    length = 0
    for num, char in enumerate(text):
        if length > 70:
            if text[num] == ' ':
                result += '\n'
                length = 0
                char = ''
        elif length > 90:
            result += '\n'
            length = 0
        if text[num:num + 1] == '\n':
            length = -1
        length += 1
        if char == ':':
            result += '\:'
        else:
            result += char
    return result


def extend(config: Config):
    video_path = Path('/'.join(config.audio_path.split('/')[:-1]))
    glob = config.audio_path.split('/')[-1]
    flist = fileglob(video_path, glob)
    random.shuffle(flist)

    if config.timeout:
        stop_time = datetime.now() + timedelta(minutes=config.timeout)
    else:
        stop_time = None

    config.extension = Extension(flist=flist, stop_time=stop_time)

    with open("youtube.key", "w") as text_file:
        print(config.youtube_key, file=text_file)

    return config


def get_pray(config, num):
    promises = [
        'Ибо только Я знаю намерения, какие имею о вас, говорит Господь, '
        'намерения во благо, не на зло, чтобы дать вам будущность и надежду.\nИер. 29,11.',
        'Посему, братия, более и более старайтесь делать твёрдым ваше звание и избрание; так поступая никогда '
        'не преткнётесь, ибо так откроется вам свободный вход в вечное Царство Господа нашего и '
        'Спасителя Иисуса Христа.\n2 Петра 1:10-11',
        'Ибо так возлюбил Бог мир, то отдал Сына Своего Единородного, дабы всякий верующий в Него, не погиб, но имел '
        'жизнь вечную.\nИоанна 3:16',
        'Побеждающий облечётся в белые одежды, и не изглажу имени его из книги жизни, и исповедаю имя его пред Отцем '
        'Моим и пред Ангелами Его.\nОткр. 3:5',
        'С великою радостью принимайте, братия мои, когда впадаете в различные искушения, зная, что испытание вашей '
        'веры производит терпение. Терпение же должно иметь совершенное действие, чтобы вы были совершенны во всей '
        'полноте, без всякого недостатка\nИакова 1:2-4',
        'Бог же всякой благодати, призвавший нас в вечную славу Свою во Христе Иисусе, Сам, по кратковременном '
        'страдании вашем, да совершит вас, да утвердит, да укрепит, да соделает непоколебимыми.\n1 Петра 5 10',
        'Ибо кратковременное легкое страдание наше производит в безмерном преизбытке вечную славу, когда мы смотрим не '
        'на видимое, но на невидимое\: ибо видимое временно, а невидимое вечно.\n2 Кор. 4\:17-18',
        'Ибо кого Он предузнал, тем и предопределил быть подобными образу Сына Своего, дабы Он был первородным между '
        'многими братиями.\nРимл. 8:29',
        'Посему и мы, имея вокруг себя такое облако свидетелей, свергнем с себя всякое бремя и запинающий нас грех и с '
        'терпением будем проходить предлежащее нам поприще, взирая на начальника и совершителя веры Иисуса, Который '
        'вместо предлежавшей Ему радости, претерпел крест, пренебрегши посрамление, и воссел одесную престола '
        'Божия.\nЕвр. 12:1-2',
        'И отрёт Бог всякую слезу с очей их, и смерти не будет уже; ни плача, ни вопля, ни болезни уже не будет, '
        'ибо прежнее прошло.\nОткр. 21:4',
        'Побеждающий наследует всё, и буду ему Богом, и он будет Мне сыном.\nОткр. 21:7',
        'Не бойся, ибо Я с тобою; не смущайся, ибо Я Бог твой; Я укреплю тебя, и помогу тебе, и поддержу тебя десницею '
        'правды Моей.\nИсаии 41:10',
        'Итак покоритесь Богу; противостаньте диаволу, и убежит от вас. Приблизьтесь к Богу, и приблизится к вам.'
        '\nИакова 4:7-8',
        'Господь Сам пойдёт пред тобою, Сам будет с тобою, не отступит от тебя и не оставит тебя, не бойся '
        'и не ужасайся.\nВтороз. 31:8',
    ]
    pray_text = random.choice(promises)
    return f"|{pray_text}"


def proceed_stream(config: Config):
    logging.info('proceed_stream')
    while True:
        for num, audio in enumerate(config.extension.flist):
            pray_text = get_pray(config, num)
            try:
                caption = meta_caption(TinyTag.get(str(audio)))
                caption += pray_text
            except LookupError:
                caption = pray_text

            with patch.object(Ffmpeg, 'drawtext', Fake.draw_pray):
                s = FileIn(Path('pylivestream.ini'), 'youtube',
                           infn=audio, loop=False, image=config.default_background, caption=caption, yes=True)
            # TODO without caption run too slow (without -codec:v libx264 -pix_fmt yuv420p -preset ultrafast -b:v 2000)
            # TODO Òû âåñü ìèð äëÿ ìåíÿ - http://fon-ki.com/ - 4UBAND (4f41e4c07167a1.mp3)
            logging.info(audio)
            logging.info(caption)
            s.golive()

            if config.extension.stop_time and datetime.now() > config.extension.stop_time:
                logging.info('playing timeout, stop.')
                return True
            elif config.extension.stop_time:
                logging.info(f"{int((config.extension.stop_time - datetime.now()).seconds / 60)} minutes left")
