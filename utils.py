"""filling.py ?"""
from datetime import datetime, timedelta
from pathlib import Path
import random
from pylivestream import FileIn

from pylivestream.glob import fileglob
from pylivestream.utils import meta_caption
from tinytag import TinyTag

from serializers import Config, Extension


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
    return config

def get_pray(config, num):
    pray_text = "Молитвенная нужда, длинный текст, очень длинный текст, чтобы не вошел в один экран" \
                "\nА ещё с переносами строк\nи вообще много чего понаписали\nсмайлики, эмодзи 🙂💼⚖️✈️️✋✊"
    pray_text = "Ладно, сначала короткий протестим"
    pray_text = f"|{pray_text}"
    pray_text = ''
    return pray_text


def proceed_stream(config: Config):
    while True:
        for num, audio in enumerate(config.extension.flist):
            # TODO log playing files
            pray_text = get_pray(config, num)
            try:
                caption = meta_caption(TinyTag.get(str(audio)))
                caption += pray_text
                print(caption)
            except LookupError:
                caption = pray_text

            s = FileIn(Path('pylivestream.ini'), 'youtube',
                       infn=audio, loop=False, image=config.default_background, caption=caption, yes=True)
            # TODO insert pray here
            s.golive()

            if config.extension.stop_time and datetime.now() > config.extension.stop_time:
                print('playing timeout, stop.')
                return True
            elif config.extension.stop_time:
                print(int((config.extension.stop_time - datetime.now()).seconds / 60), 'minutes left')
