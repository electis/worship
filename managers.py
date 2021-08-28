from environs import Env
import requests
from serializers import Config


def get_config():
    env = Env()
    env.read_env()
    config = Config(
        youtube_key=env('youtube_key'),
        default_background=env('default_background'),
        audio_path=env('audio_path'),
        timeout=env.int('timeout'),
        hours=env.list('hours', [], subcast=int),
        google_api_key=env('GOOGLE_API_KEY', None),
        tg_chat_id=env('TGRAM_CHATID', None),
        tg_token=env('TGRAM_TOKEN', None),
    )
    return config
