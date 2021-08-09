from environs import Env
import requests
from serializers import Config


def get_config():
    env = Env()
    env.read_env()
    config = Config(
        youtube_key = env('youtube_key'),
        default_background = env('default_background'),
        audio_path = env('audio_path'),
    )
    return config
