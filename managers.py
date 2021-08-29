from datetime import datetime, timedelta
from pathlib import Path

import random
from environs import Env
import requests
from pylivestream.glob import fileglob

from serializers import Config, Extension


class ConfigManager:
    _config: Config

    def __init__(self):
        self._config = self.get_config()

    @property
    def hours(self):
        return self._config.hours

    @property
    def tg(self):
        return self._config.tg

    @property
    def extension(self):
        if self._config.extension:
            return self._config.extension
        return self.extend().extension

    def get_config(self):
        env = Env()
        env.read_env()
        config = Config(
            youtube_key=env('youtube_key'),
            default_background=env('default_background'),
            audio_path=env('audio_path'),
            timeout=env.int('timeout'),
            hours=env.list('hours', [], subcast=int),
            google_api_key=env('GOOGLE_API_KEY', None),
        )
        tg = dict(
            tg_chat_id=env('TGRAM_CHATID', None),
            tg_token=env('TGRAM_TOKEN', None),
        )
        if tg['tg_chat_id'] and tg['tg_token']:
            config.tg = tg
        self._config = config
        return config

    def extend(self):
        config = self._config
        video_path = Path('/'.join(config.audio_path.split('/')[:-1]))
        glob = config.audio_path.split('/')[-1]
        flist = fileglob(video_path, glob)
        random.shuffle(flist)

        if config.timeout:
            stop_time = datetime.now() + timedelta(minutes=config.timeout)
        else:
            stop_time = None

        config.extension = Extension(flist=flist, stop_time=stop_time, default_background=config.default_background)

        with open("youtube.key", "w") as text_file:
            print(config.youtube_key, file=text_file)

        return config
