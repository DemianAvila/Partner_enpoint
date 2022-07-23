from pydantic import BaseModel, Extra, validator, ValidationError
from typing import Optional

#REQUEST MODEL TYPING TEMPLATE
class RoutesFilter(BaseModel, extra=Extra.forbid):
    route_name: Optional[str] = None
    route_id: Optional[int] = None
    partner_name: Optional[str] = None
    partner_id: Optional[int] = None
    available: Optional[bool] = True
    active: Optional[bool] = True

    def __getitem__(self, item):
        return getattr(self, item)

class RoutesAcceptSearch(BaseModel, extra=Extra.forbid):
    case_sensitive: Optional[bool] = False
    reg_exp: Optional[bool] = True

class RoutesRequestModel(BaseModel, extra=Extra.forbid):
    filters: Optional['RoutesFilter'] = None
    order_by: Optional[str] = None
    accept: Optional['RoutesAcceptSearch'] = None
 
    @validator('order_by')
    def parameters(cls, v):
        values = ["name", "zone", "code", "distance", 
            "partner", "start_date", "end_date", None]

        if v not in values:
            raise ValueError(f"Order parameter '{v}' not valid")

        else:
            return v
