import os
from pathlib import Path

import pylivestream.api as pls


def stream(audio_path: str, background_file: str, use_meta=None):
    pls.stream_files(
        Path('pylivestream.ini'), 'youtube',
        video_path=Path('/'.join(audio_path.split('/')[:-1])),
        still_image=Path(background_file),
        glob=audio_path.split('/')[-1],
        loop=True,
        shuffle=True,
        assume_yes=True,
        no_meta=use_meta,
    )


if __name__ == '__main__':
    audio_path = os.getenv('audio_path', '/storage/download/music/worship/*.mp3')
    background_file = os.getenv('background_file', '/storage/download/music/church.jpg')
    stream(audio_path, background_file, os.getenv('use_meta'))
