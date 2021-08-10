"""filling.py ?"""
from datetime import datetime, timedelta
from pathlib import Path
import random

from pylivestream.glob import fileglob

from serializers import Config


def extend(config: Config):
    video_path = Path('/'.join(config.audio_path.split('/')[:-1]))
    glob = config.audio_path.split('/')[-1]
    flist = fileglob(video_path, glob)
    random.shuffle(flist)
    config.extension.flist = flist

    if config.timeout:
        stop_time = datetime.now() + timedelta(minutes=config.timeout)
    else:
        stop_time = None
    config.extension.stop_time = stop_time
    return config


def proceed_stream(config: Config):
    ...
