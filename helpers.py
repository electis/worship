from datetime import datetime, timedelta
from pathlib import Path
import random
import typing as T
from unittest.mock import patch

from pylivestream.glob import fileglob

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None
from pylivestream.base import FileIn
from pylivestream.utils import meta_caption
from pylivestream.ffmpeg import Ffmpeg


class Fake:

    def drawtext(self, text: str = None) -> T.List[str]:
        # fontfile=/path/to/font.ttf:
        if not text:  # None or '' or [] etc.
            return []

        fontcolor = "fontcolor=white"
        fontsize = "fontsize=24"
        box = "box=1"
        boxcolor = "boxcolor=black@0.5"
        border = "boxborderw=5"
        x = "x=(w-text_w)/2"
        y = "y=(h-text_h)*3/4"

        return [
            "-vf",
            f"drawtext=text='{text}':{fontcolor}:{fontsize}:{box}:{boxcolor}:{border}:{x}:{y}",
        ]


@patch.object(Ffmpeg, 'drawtext', Fake.drawtext)
def playonce(
        flist: T.List[Path],
        image: Path,
        sites: T.Sequence[str],
        inifn: Path,
        shuffle: bool,
        usemeta: bool,
        stop_time,
):
    if shuffle:
        random.shuffle(flist)

    caption: T.Union[str, None]

    for f in flist:
        if usemeta and TinyTag:
            # TODO добавлять молитвенные нужды
            try:
                caption = meta_caption(TinyTag.get(str(f)))
                # caption += "\\nМолитвенная нужда 1\\n\\nМолитвенная нужда 2\\n\\nИ т.д."
                print(caption)
            except LookupError:
                caption = None
        else:
            caption = None

        s = FileIn(inifn, sites, infn=f, loop=False, image=image, caption=caption, yes=True)

        s.golive()

        if stop_time:
            if datetime.now() > stop_time:
                print('playing timeout, stop.')
                return True
            else:
                print(int((stop_time - datetime.now()).seconds / 60), 'minutes left')


def stream_files(
        ini_file: Path,
        websites: T.Sequence[str],
        *,
        video_path: Path,
        glob: str = None,
        loop: bool = None,
        shuffle: bool = None,
        still_image: Path = None,
        usemeta: bool = None,
        timeout: int = None,
):
    flist = fileglob(video_path, glob)

    print("streaming these files. Be sure list is correct! \n")
    print("\n".join(map(str, flist)), "\n")
    print("going live on", websites)

    if timeout:
        stop_time = datetime.now() + timedelta(minutes=timeout)
    else:
        stop_time = None

    if loop:
        while True:
            if playonce(flist, still_image, websites, ini_file, shuffle, usemeta, stop_time=stop_time):
                return True
    else:
        playonce(flist, still_image, websites, ini_file, shuffle, usemeta, stop_time=stop_time)
