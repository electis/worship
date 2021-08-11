import time
from datetime import datetime
from pathlib import Path

from helpers import stream_files
from managers import get_config
from serializers import Config
from utils import extend, proceed_stream


def stream(audio_path: str, background_file: str, use_meta: bool = None):
    stream_files(
        Path('pylivestream.ini'), 'youtube',
        video_path=Path('/'.join(audio_path.split('/')[:-1])),
        still_image=Path(background_file),
        glob=audio_path.split('/')[-1],
        loop=True,
        shuffle=True,
        usemeta=use_meta,
        timeout=60
    )


def proceed_worship():
    config: Config = get_config()
    config = extend(config)
    while True:
        if datetime.now().hour in (7, 10, 13, 16, 19):
            proceed_stream(config)
        else:
            time.sleep(30)


if __name__ == '__main__':
    proceed_worship()
    # audio_path = os.getenv('audio_path', '/storage/download/music/worship/*.mp3')
    # background_file = os.getenv('background_file', '/storage/download/music/church.jpg')
    # stream(audio_path, background_file, os.getenv('use_meta', True))
