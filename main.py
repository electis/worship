import time
from datetime import datetime
from pathlib import Path

from helpers import stream_files
from managers import get_config
from serializers import Config
from utils import extend, proceed_stream, log_tg


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
    if config.hours:
        while True:
            if datetime.now().hour in config.hours:
                log_tg('Worship start', config)
                proceed_stream(config)
                log_tg('Worship end', config)
            else:
                time.sleep(30)
    else:
        log_tg('Worship start', config)
        proceed_stream(config)
        log_tg('Worship end', config)

if __name__ == '__main__':
    proceed_worship()
    # audio_path = os.getenv('audio_path', '/storage/download/music/worship/*.mp3')
    # background_file = os.getenv('background_file', '/storage/download/music/church.jpg')
    # stream(audio_path, background_file, os.getenv('use_meta', True))
