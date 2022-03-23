from datetime import datetime, timedelta
import json
from pathlib import Path

import logging
import random
from environs import Env
import requests
from pylivestream.glob import fileglob

from serializers import Config, Extension, TG
from utils import log_tg


class ConfigManager:
    _config: Config

    def __init__(self):
        self._config = self.get_config()

    @property
    def hours(self):
        return self._config.hours

    @property
    def days(self):
        return self._config.days

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
        env.read_env(override=True)
        config = Config(
            server_key=env('server_key', env('youtube_key', None)),
            server_name=env('server_name', 'youtube'),
            default_background=env('default_background'),
            audio_path=env('audio_path'),
            timeout=env.int('timeout'),
            hours=env.list('hours', [], subcast=int),
            days=env.list('days', [], subcast=int),
            google_api_key=env('GOOGLE_API_KEY', None),
            task_url=env('task_url', None),
            task_token=env('task_token', None),
            youtube_channel=env('youtube_channel', None),
            chat_id=env('chat_id', None),
            delta_minutes=env.int('delta_minutes', 7),
        )
        tg = TG(
            tg_chat_id=env('TGRAM_CHATID', None),
            tg_token=env('TGRAM_TOKEN', None),
        )
        if tg.tg_chat_id and tg.tg_token:
            config.tg = tg
        self._config = config
        return config

    @staticmethod
    def load_bible(raise_exception=False):
        try:
            with open('bible.txt') as f:
                return json.load(f)
        except Exception as exc:
            logging.warning(str(exc))
            if raise_exception:
                raise

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

        config.extension = Extension(
            flist=flist, stop_time=stop_time, default_background=config.default_background, promises=self.load_bible(),
            server_name=config.server_name
        )

        with open(f"{config.server_name}.key", "w") as text_file:
            print(config.server_key, file=text_file)

        return config

    def run_task(self, params):
        if self._config.task_url and self._config.task_token:
            try:
                from requests.adapters import HTTPAdapter
                s = requests.Session()
                s.mount(self._config.task_url, HTTPAdapter(max_retries=5))
                s.post(self._config.task_url, headers=dict(Authorization=f'Token {self._config.task_token}'),
                       json=params)
            except Exception:
                requests.post(self._config.task_url, headers=dict(Authorization=f'Token {self._config.task_token}'),
                              json=params)
                raise

    def post2group(self):
        if self._config.youtube_channel and self._config.chat_id:
            params = {
                # "task": "post2group",
                "task": "start_worship",
                "delta_time": f"{self._config.delta_minutes}:00",
                "params": {
                    "chat_id": self._config.chat_id,
                    "text": "Время молитвы",
                    # "delete_after": "23:55:00",
                    "youtube_live": self._config.youtube_channel,
                    "youtube_filter": "Время молитвы"
                }
            }
            try:
                self.run_task(params)
            except Exception as exc:
                logging.warning(str(exc))
                log_tg(f'post2group {exc}', self._config.tg)
