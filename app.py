import models.request_routes_models as request_models
import models.response_routes_models as response_models
import modules.multi_purpose_functions as multi_purpose
from odooly import Client
from fastapi import FastAPI, Request, Response, status
from pydantic import ValidationError
from datetime import datetime, date
app = FastAPI()

# MUST CHANGE TO THE ENV FILE
client = Client(server = "http://localhost:8069", 
    db = "trx_business", 
    user = "admin", 
    password = "admin"
)
  
    
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
        req_validation = request_models.RoutesRequestModel(**req)
    except ValidationError as e:
        for error in e.errors():
            response.status_code = status.HTTP_400_BAD_REQUEST
            if str(error['type'])=="value_error.extra":
                return {
                    "DESCRIPTION": f"{error['loc']} field(s) are not accepted in this endpoint"
                }
            elif str(error['type'])=="value_error":
                return {
                    "DESCRIPTION": str(error['msg'])
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
            print(_filter)
            if req_validation.filters[_filter] != None and req_validation.filters[_filter] != False:
                print("enabled")
                enabled_filters.append(_filter)

    #print(f"enabled -> {enabled_filters}")
    #print(f"fields -> {req_validation.filters.__fields__.keys()}")

    #ITERATE OVER ALL RECORDS
    for index, route in enumerate(routes):
        #SEARCH PARTNER DATA
        if route.partner != False:
            partner = client.env['res.partner'].search([('id', '=', route.partner.id)])
            #GET THE ONLY PARTNER
            if len(partner)==1:
                partner = partner[0]
            else:
                partner = None
        else:
            partner = ""
        #CHECK ROUTE NAME
        #WHERE CONDITION DON'T MEET, REMOVE
        if 'route_name' in enabled_filters:
            if not multi_purpose.multi_comparison(reg_exp = reg_exp, 
                case_sensitive = case_sensitive, 
                first_comp = route.name, 
                second_comp = req_validation.filters.route_name
            ):
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK ROUTE ID
        print()
        if 'route_id' in enabled_filters:
            if route.id != req_validation.filters.route_id:
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK PARTNER NAME
        if 'partner_name' in enabled_filters:
            if not multi_purpose.multi_comparison(reg_exp = reg_exp,
                case_sensitive = case_sensitive,
                first_comp = partner.name,
                second_comp = req_validation.filters.partner_name
            ):
                routes = list(filter(lambda x: x.id != route.id ,routes))
                continue
        #CHECK PARTNER ID
        if 'partner_id' in enabled_filters:
            if route.id != req_validation.filters.partner_id:
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
    resp = response_models.RoutesResponse(routes = [])
    for route in routes:
        route_id = route.id
        #SET NAME FIELD
        if route.name == False:
            name = ''
        else:
            name = route.name
        #SET PARTNER FIELD
        if route.partner == False:
            partner_info = response_models.PartnerInfo(partner_id = None,
                partner_name = 'Undefined')
        else:
            partner_info = response_models.PartnerInfo(partner_id = route.partner.id,
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
                response_models.StationInfo(
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
                    response_models.Rating(
                        commenter = multi_purpose.change_false(rating.commenter),
                        score = multi_purpose.change_false(rating.score),
                        comment = multi_purpose.change_false(rating.comment)
                    )
                )
            stations_schedule = []
            for station in trip.stations:
                if station.station_name == False:
                    stations_schedule.append(
                        response_models.TripStation(
                            station_id = None,
                            init_date = ""
                        )
                    )
                else:
                    stations_schedule.append(
                        response_models.TripStation(
                            station_id = multi_purpose.change_false(station.station_name.id),
                            init_date = multi_purpose.change_false(station.start_hour)
                        )
                    )
            if trip.driver_id == False:
                driver = response_models.DriverInfo(
                    driver_id = None,
                    driver_full_name = "Not defined yet"
                )
            else:
                driver = response_models.DriverInfo(
                    driver_id = multi_purpose.change_false(trip.driver_id.id),
                    driver_full_name = f"{multi_purpose.change_false(trip.driver_id.name)} {multi_purpose.change_false(trip.driver_id.last_name)}".strip()
                )

            if trip.vehicle_id == False:
                vehicle = response_models.VechicleInfo(
                    vehicle_id = None,
                    vin = "",
                    plate = "",
                    brand = "",
                    model = ""
                )

            else:
                vehicle = response_models.VechicleInfo(
                    vehicle_id = multi_purpose.change_false(trip.vehicle_id.id),
                    vin = multi_purpose.change_false(trip.vehicle_id.vin_sn),
                    plate = multi_purpose.change_false(trip.vehicle_id.licence_plate),
                    brand = multi_purpose.change_false(trip.vehicle_id.model_id.brand_id.name),
                    model = multi_purpose.change_false(trip.vehicle_id.model_id.name)
                )
            

            trips.append(response_models.TripInfo(
                vehicle = vehicle,
                driver = driver,
                init_date = multi_purpose.change_false(trip.startDate),
                end_date = multi_purpose.change_false(trip.endDate),
                seats = trip.seats,
                stations_schedule = stations_schedule,
                ratings = ratings
                )
            )


        resp.routes.append(
            response_models.RouteInfo(
                route_id = route_id,
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

