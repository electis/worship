from datetime import datetime, timedelta
from pathlib import Path
import random
import typing as T

from pylivestream.glob import fileglob

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None
from pylivestream.base import FileIn
from pylivestream.utils import meta_caption


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
            try:
                caption = meta_caption(TinyTag.get(str(f)))
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
                print(stop_time - (datetime.now()).seconds, 'seconds left')


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
