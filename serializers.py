from datetime import datetime
from pathlib import PosixPath
from typing import Optional, List, NewType

from pydantic import BaseModel

_Url = NewType('_Url', str)


def URL(s: str) -> _Url:
    if not s.startswith('https://'):
        raise AssertionError(s)
    ...
    return _Url(s)


class Prayer(BaseModel):
    ...


class Stream(BaseModel):
    start_time: int
    duration: int
    picture: str


class Extension(BaseModel):
    flist: List[PosixPath]
    stop_time: Optional[datetime]
    default_background: str
    promises: Optional[List[str]]


class TG(BaseModel):
    tg_chat_id: Optional[str]
    tg_token: Optional[str]

class Config(BaseModel):
    youtube_key: str
    default_background: str
    audio_path: str
    timeout: Optional[int]
    google_api_key: Optional[str]
    hours: Optional[list]
    prayers: Optional[List[Prayer]]
    ini: Optional[str]
    extension: Optional[Extension]
    tg: Optional[TG]
    streams: Optional[Stream]
