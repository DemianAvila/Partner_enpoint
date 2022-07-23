from pydantic import BaseModel, Extra
from typing import Optional, List


#RESPONSE MODEL TYPING TEMPLATE
class PartnerInfo(BaseModel, extra=Extra.forbid):
    partner_id: Optional[int] = None
    partner_name: Optional[str] = None

class DriverInfo(BaseModel, extra=Extra.forbid):
    driver_id: Optional[int] = None
    driver_full_name: Optional[str] = "Not defined yet"

class VechicleInfo(BaseModel, extra=Extra.forbid):
    vehicle_id: Optional[int] = None 
    vin: Optional[str] = None
    plate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None

class StationInfo(BaseModel, extra=Extra.forbid):
    station_id: Optional[int] = None
    station_name: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[str] = None
    lon: Optional[str] = None

class TripStation(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    station_id: Optional[int] = None
    init_date: Optional[str] = None 

class Rating(BaseModel, extra=Extra.forbid):
    commenter: Optional[str] = None
    score: Optional[int] = None
    comment: Optional[str] = None

class TripInfo(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    vehicle: Optional['VechicleInfo'] = None
    driver: Optional['DriverInfo'] = None
    init_date: Optional[str] = None
    end_date: Optional[str] = None
    seats: Optional[int] = None
    stations_schedule: Optional[List['TripStation']] = None
    ratings: Optional[List['Rating']] = None

class RouteInfo(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    route_id: int
    name: Optional[str] = None
    partner: Optional[PartnerInfo] = None
    zone: Optional[str] = None
    code:  Optional[str] = None
    init_date: Optional[str] = None
    end_date: Optional[str] = None 
    stations: Optional[List['StationInfo']] = None
    trips: Optional[List['TripInfo']] = None

class RoutesResponse(BaseModel, extra=Extra.forbid):
    DESCRIPTION: Optional[str] = "OK"
    routes: Optional[List['RouteInfo']] = None


