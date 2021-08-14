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
        y = f"y=h*{part}+(text_h+20)*{row}"
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
        if length > 80:
            result += '\n'
            length = 0
        if text[num:num + 1] == '\n':
            length = -1
        length += 1
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
    pray_text = "Молитвенная нужда, длинный текст, очень длинный текст, чтобы не вошел в один экран" \
                " ещё длиннее\nи с переносами строк, lorem ipsum"*3

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
