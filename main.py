import time
from datetime import datetime
from pathlib import Path
import sys

from helpers import stream_files
from managers import ConfigManager
from utils import proceed_stream, notify


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


def proceed_worship(arg=None):
    config = ConfigManager()
    if config.hours and arg != 'now':
        minutes = 0
        while True:
            now = datetime.now()
            proceed_time: bool = now.hour in config.hours
            proceed_days: bool = True if not config.days else now.weekday() in config.days
            if proceed_time and proceed_days:
                with notify('Worship', config.tg):
                    config.post2group()
                    proceed_stream(config.extension)
            else:
                time.sleep(60)
                minutes += 1
            if minutes == 5:
                config.get_config()
                minutes = 0
    else:
        with notify('Worship', config.tg):
            config.post2group()
            proceed_stream(config.extension)

if __name__ == '__main__':
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else None
    print('Available param: now', f'Param: {arg}')
    proceed_worship(arg)
