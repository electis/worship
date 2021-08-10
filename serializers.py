from typing import Optional, Union, Literal, List
from typing import NewType

from datetime import datetime
from pydantic import BaseModel

_Url = NewType('_Url', str)


def URL(s: str) -> _Url:
    if not s.startswith('https://'):
        raise AssertionError(s)
    ...
    return _Url(s)


class Prayer(BaseModel):
    ...


class Extension(BaseModel):
    flist = List[str]
    stop_time: Optional[datetime]


class Config(BaseModel):
    prayers: Optional[List[Prayer]]
    youtube_key: str
    default_background: str
    ini: Optional[str]
    audio_path: str
    timeout: Optional[int]
    extension = Optional[Extension]
