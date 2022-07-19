from odooly import Client
from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel, Extra, ValidationError
from typing import Optional, List
from datetime import datetime, date
import re
app = FastAPI()

# MUST CHANGE TO THE ENV FILE
client = Client(server = "http://localhost:8069", 
    db = "trx_business", 
    user = "admin", 
    password = "admin"
)
#-----------------------------------------------
#MULTIPROPOUSE FUNCTIONS
def multi_comparison(reg_exp, case_sensitive, first_comp, second_comp):
    if first_comp == None or first_comp==False:
        first_comp = ''
    if second_comp==None or second_comp==False:
        second_comp = ''

    #IF STRING DON'T MATCH, RETURN FALSE
    #WITH CASE SENSITIVE AND NO REGEXP
    if not reg_exp and case_sensitive:
        if first_comp != second_comp:
            return False
            
    #WITH NO CASE SENSITIVE AND NO REGEXP
    if not reg_exp and not case_sensitive:
        if first_comp.upper() != second_comp.upper():
            return False
            
    #WITH CASE SENSITIVE AND REGEXP
    if reg_exp and case_sensitive: 
        if not re.search(second_comp, first_comp):
            return False
            
    #WITH NO CASE SENSITIVE AND REGEXP
    if reg_exp and not case_sensitive:
        if not re.search(second_comp, first_comp.upper()):
            return False
           
    #IF FILTERS PASS, RETURN TRUE
    return True

def change_false(field):
    if field == False:
        return ""
    else:
        return field
#-------------------------------------------------

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

    
#ENDPOINTS
@app.get('/get_routes')
async def get_routes(request: Request, 
    response: Response):
    #TRY TO GET THE REQUEST BODY
    try:
        req = await request.json()
    except Exception as e:
        response.status_code = status.HTTP_408_REQUEST_TIMEOUT
        return {
            "DESCRIPTION": "Timeout, could not get the request",
            "EXCEPTION": str(e)
        }

    #MATCH THE REQUEST TO THE MODEL
    try:
        req_validation = RoutesRequestModel(**req)
    except ValidationError as e:
        for error in e.errors():
            if str(error['type'])=="value_error.extra":
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {
                    "DESCRIPTION": f"{error['loc']} field(s) are not accepted in this endpoint"
                }

    #TRY TO READ THE ODOO ROUTE'S MODEL
    try:        
        routes = list(client.env['trx_bus_traxi.routes'].search([]))
    except Exception as e:
        response.status_code = status.HTTP_408_REQUEST_TIMEOUT
        return {
            "DESCRIPTION": "Timeout, no connection to database",
            "EXCEPTION": str(e)
        }

    #-------------------------------------
    #FILTER THE RESULTS OF THE MODEL
    #FLAG OF REGEXP AND CASE SENSITIVE
    print(req_validation)
    if req_validation.accept != None:
        if req_validation.accept.reg_exp == True: 
            reg_exp = True
        else:
            reg_exp = False
        if req_validation.accept.case_sensitive == True:
            case_sensitive = True
        else:
            case_sensitive = False
    else:
        reg_exp = True
        case_sensitive = False 
    #ENABLED FILTERS
    enabled_filters = []
    if req_validation.filters != None:
        for _filter in req_validation.filters.__fields__.keys():
            if req_validation.filters[_filter] != None and req_validation.filters[_filter] != False:
                enabled_filters.append(_filter)

    #ITERATE OVER ALL RECORDS
    for index, route in enumerate(routes):
        #SEARCH PARTNER DATA
        partner = client.env['res.partner'].search([('id', '=', route.partner.id)])
        #GET THE ONLY PARTNER
        if len(partner)==1:
            partner = partner[0]
        else:
            partner = None
        #CHECK ROUTE NAME
        #WHERE CONDITION DON'T MEET, REMOVE
        if 'route_name' in enabled_filters:
            if not multi_comparison(reg_exp = reg_exp, 
                case_sensitive = case_sensitive, 
                first_comp = route.name, 
                second_comp = req_validation.filters.route_name
            ):
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK ROUTE ID
        if 'route_id' in enabled_filters:
            if route.id != request['filters']['route_id']:
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK PARTNER NAME
        if 'partner_name' in enabled_filters:
            if not multi_comparison(reg_exp = reg_exp,
                case_sensitive = case_sensitive,
                first_comp = partner.name,
                second_comp = req_validation.filters.partner_name
            ):
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK PARTNER ID
        if 'partner_id' in enabled_filters:
            if route.id != request.filters.partner_id:
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK IF ROUTE AVAILABLE
        if 'available' in enabled_filters:
            if route.availableRoute != 'available':
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK IF ROUTE ACTIVE
        if 'active' in enabled_filters:
            #PARSE TO DATE
            since = list(map(lambda x: int(x.strip()),route.effectiveDateSince.split('-')))
            since = datetime(day=since[2], month=since[1], year=since[0])
            until = list(map(lambda x: int(x.strip()),route.effectiveDateUntil.split('-')))
            until = datetime(day=until[2], month=until[1], year=until[0])
            if datetime.today() < since or datetime.today() > until:
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue

    #ITERATE OVER THE ROUTES AT THE END OF FILTERS
    resp = RoutesResponse(routes = [])
    for route in routes:
        #SET NAME FIELD
        if route.name == False:
            name = ''
        else:
            name = route.name
        #SET PARTNER FIELD
        if route.partner == False:
            partner_info = PartnerInfo(partner_id = None,
                partner_name = 'Undefined')
        else:
            partner_info = PartnerInfo(partner_id = route.partner.id,
                partner_name = route.partner.name)
        #SET ZONE FIELD
        if route.zone == False:
            zone = ''
        else:
            zone = route.zone
        #SET CODE FIELD
        if route.code == False:
            code = ''
        else:
            code = route.code
        #SET INIT DATE FIELD
        if route.effectiveDateSince == False:
            since = ''
        else:
            since = route.effectiveDateSince
        #SET END DATE FIELD
        if route.effectiveDateUntil == False:
            until = ''
        else:
            until = route.effectiveDateUntil
        #SET STATIONS
        stations = []
        for station in route.stations:
            if station.id==None:
                station_id = None
            else:
                station_id = station.id
            if station.name == False:
                station_name = ""
            else:
                station_name = station.name
            if station.address == False:
                station_address = ""
            else:
                station_address = station.address
            if station.latitude == False:
                station_latitude = ""
            else:
                station_latitude = station.latitude
            if station.longitude == False:
                station_longitude = ""
            else:
                station_longitude = station.longitude

            stations.append(
                StationInfo(
                    station_id = station_id,
                    station_name = station_name,
                    address = station_address,
                    lat = station_latitude,
                    lon = station_longitude
                )
            )
        #SET TRIPS
        trips = []
        for trip in route.trips:
            #RATINGS PER TRIP
            ratings = []
            for rating in trip.comments:
                ratings.append(
                    Rating(
                        commenter = change_false(rating.commenter),
                        score = change_false(rating.score),
                        comment = change_false(rating.comment)
                    )
                )
            stations_schedule = []
            for station in trip.stations:
                if station.station_name == False:
                    stations_schedule.append(
                        TripStation(
                            station_id = None,
                            init_date = ""
                        )
                    )
                else:
                    stations_schedule.append(
                        TripStation(
                            station_id = change_false(station.station_name.id),
                            init_date = change_false(station.start_hour)
                        )
                    )
            if trip.driver_id == False:
                driver =DriverInfo(
                    driver_id = None,
                    driver_full_name = "Not defined yet"
                )
            else:
                driver = DriverInfo(
                    driver_id = change_false(trip.driver_id.id),
                    driver_full_name = f"{change_false(trip.driver_id.name)} {change_false(trip.driver_id.last_name)}".strip()
                )

            if trip.vehicle_id == False:
                vehicle = VechicleInfo(
                    vehicle_id = None,
                    vin = "",
                    plate = "",
                    brand = "",
                    model = ""
                )

            else:
                vehicle = VechicleInfo(
                    vehicle_id = change_false(trip.vehicle_id.id),
                    vin = change_false(trip.vehicle_id.vin_sn),
                    plate = change_false(trip.vehicle_id.licence_plate),
                    brand = change_false(trip.vehicle_id.model_id.brand_id.name),
                    model = change_false(trip.vehicle_id.model_id.name)
                )
            

            trips.append(TripInfo(
                vehicle = vehicle,
                driver = driver,
                init_date = change_false(trip.startDate),
                end_date = change_false(trip.endDate),
                seats = trip.seats,
                stations_schedule = stations_schedule,
                ratings = ratings
                )
            )


        resp.routes.append(
            RouteInfo(
                name = name,
                partner = partner_info,
                zone = zone,
                code = code,
                init_date = since,
                end_date = until,
                stations = stations,
                trips =  trips
            )
        )
    #-------------------------------------------------
    response.status_code = status.HTTP_200_OK
    """
    resp = {
        "DESCRIPTION": "OK",
        "routes":[]
    }

    for route in routes:
        resp['routes'].append({
                "name": route.name
            }
        )
    """
    return resp

