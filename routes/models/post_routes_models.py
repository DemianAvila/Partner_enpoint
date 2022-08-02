from pydantic import BaseModel, Extra
from typing import Optional, List


#POST MODELS

class Stations(BaseModel, extra=Extra.forbid):
    name: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[str] = None
    lon: Optional[str] = None

class IgnoreRepeated(BaseModel, extra=Extra.forbid):
    name: Optional[bool] = False
    code: Optional[bool] = False


class PostRoute(BaseModel, extra=Extra.forbid):
    name: Optional[str] = None
    partner_id: Optional[int] = None
    zone: Optional[str] = None
    code: Optional[str] = None
    init_date: Optional[str] = None
    end_date: Optional[str] = None
    ignored_repeated: Optional["IgnoreRepeated"] = IgnoreRepeated()
    stations: Optional[List["Stations"]] = []
    available: Optional[bool] = True


