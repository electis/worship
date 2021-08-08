from typing import Optional, Union, Literal, List
from typing import NewType

from pydantic import BaseModel

_Url = NewType('_Url', str)


def URL(s: str) -> _Url:
    if not s.startswith('https://'):
        raise AssertionError(s)
    ...
    return _Url(s)


class Prayer(BaseModel):
    ...


class Config(BaseModel):
    prayers: Optional[List[Prayer]]
    youtube_key: str
    default_background: URL
    ini: Optional[str]
