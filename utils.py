import logging
from contextlib import contextmanager

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import random
import requests

from pylivestream import FileIn
from pylivestream.ffmpeg import Ffmpeg
from pylivestream.utils import meta_caption
from tinytag import TinyTag

from serializers import Extension

logging.basicConfig(
    filename='output.log', level=logging.INFO,
    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
)


class Fake:

    @staticmethod
    def draw_text(text: str = None, up=False, row=1) -> list:
        # fontfile=/path/to/font.ttf:
        if not text:
            return []

        _border = 4

        if up:
            _fontsize = 32
            part = '1/16'
            fontcolor = "fontcolor=yellow"
        else:
            _fontsize = 24
            part = '11/12'
            fontcolor = "fontcolor=white"
        fontsize = f"fontsize={_fontsize}"
        box = "box=1"
        boxcolor = "boxcolor=black@0.5"
        border = f"boxborderw={_border}"
        x = "x=(w-text_w)/2"
        # y = f"y=h*{part}+(text_h+20)*{row}"
        y = f"y=h*{part}+({_fontsize + _border * 2})*{row}"
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
        # TODO max_length in settings
        pray_rows = insert_line_breaks(text_list[1], max_length=65).split('\n')

        for row, string in enumerate(pray_rows, 1):
            cmd_list = Fake.draw_text(string, up=True, row=row)
            if not cmd_list:
                continue
            if not result:
                result = cmd_list
            else:
                result[1] += f', {cmd_list[1]}'

        return result


def insert_line_breaks(text: str, max_length=85):
    result = ''
    length = 0
    for num, char in enumerate(text):
        if length > max_length - max_length * 0.2:
            if text[num] == ' ':
                result += '\n'
                length = 0
                char = ''
        elif length > max_length:
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


def get_pray(extension: Extension, num):
    pray_text = random.choice(extension.promises)
    return f"|{pray_text}"


def proceed_stream(extension: Extension):
    logging.info('proceed_stream')
    while True:
        for num, audio in enumerate(extension.flist):
            pray_text = get_pray(extension, num)
            try:
                caption = meta_caption(TinyTag.get(str(audio)))
            except LookupError:
                caption = str(audio)
            caption += pray_text

            with patch.object(Ffmpeg, 'drawtext', Fake.draw_pray):
                s = FileIn(Path('pylivestream.ini'), [extension.server_name],
                           infn=audio, loop=False, image=extension.default_background, caption=caption, yes=True)
            # TODO without caption run too slow (without -codec:v libx264 -pix_fmt yuv420p -preset ultrafast -b:v 2000)
            # TODO Òû âåñü ìèð äëÿ ìåíÿ - http://fon-ki.com/ - 4UBAND (4f41e4c07167a1.mp3)
            logging.info(audio)
            logging.info(caption)
            s.golive()

            if extension.stop_time and datetime.now() > extension.stop_time:
                logging.info('playing timeout, stop.')
                return True
            elif extension.stop_time:
                logging.info(f"{int((extension.stop_time - datetime.now()).seconds / 60)} minutes left")


def send_message(text, chat_id, token, parse_mode='Markdown'):
    try:
        response = requests.get(f'https://api.telegram.org/bot{token}/sendMessage', timeout=10, params=dict(
            chat_id=chat_id, text=text, parse_mode=parse_mode))
    except Exception as exc:
        logging.warning(f'send_message Exception: {exc}')
        return False
    else:
        if response.status_code == 200:
            return response.json()
        else:
            logging.warning(f'send_message status_code {response.status_code}')
            return False


def log_tg(text, tg=None):
    if tg:
        return send_message(text, tg.tg_chat_id, tg.tg_token)
    logging.info(text)


@contextmanager
def notify(text, tg, only_error=True):
    if not only_error:
        log_tg(f'start {text}', tg)
    try:
        yield
    except Exception as exc:
        log_tg(f'Exception {exc}', tg)
    else:
        if not only_error:
            log_tg(f'stop {text}', tg)
