from .models import  post_routes_models as post_models
from odooly import Client
from fastapi import APIRouter, Request, Response, status, Depends
from pydantic import ValidationError
from datetime import datetime, date
from .modules import multi_purpose_functions as func

router = APIRouter(tags=["Routes"])

client = Client(server = "http://localhost:8069",                                     
    db = "trx_business",                                                              
    user = "admin",                                                                   
    password = "admin"                                                                
)

@router.patch('/patch_route')
async def patch_route(route: post_models.PatchRoute,                                                
    response: Response):
    #commons: post_models.PatchRoute = Depends()):
    #TRY TO GET THE REQUEST BODY                                                      
    #try:                                                                              
    #    req = await request.json()                                                    
    #except Exception as e:                                                            
    #    response.status_code = status.HTTP_408_REQUEST_TIMEOUT                        
    #    return {                                                                      
    #        "DESCRIPTION": "Timeout, could not get the request",                      
    #        "EXCEPTION": str(e)                                                       
    #    }

    #MATCH THE REQUEST TO THE MODEL                                                   
    try:                                                                              
        #req_validation = post_models.PatchRoute(**req)                     
        req_validation = route
    except ValidationError as e:                                                      
        for error in e.errors():                                                      
            print(str(error['msg']))
            response.status_code = status.HTTP_400_BAD_REQUEST                        
            if str(error['type'])=="value_error.extra":                               
                return {                                                              
                    "DESCRIPTION": f"{error['loc']} field(s) are not accepted in this endpoint"
                }                                                                     
            elif str(error['type'])=="value_error":                                   
                return {                                                              
                    "DESCRIPTION": str(error['msg'])                                  
                }
    #CHECK IF THE ROUTE ID EXISTS IN THE DATABASE
    route_id = client.env['trx_bus_traxi.routes'].search(
        [("id", "=", req_validation.route_id)]
    )
    if len(route_id)!=1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "DESCRIPTION": f"Route with id: '{req_validation.route_id}' not found"
        }
    else:
        route_id = route_id[0]
    #IF PARTNER DOESN'T EXIST, MENTION IT 
    if req_validation.partner_id != None:
        partners = client.env["res.company"].search(
            [
                (
                    'id', 
                    '=', 
                    int(req_validation.partner_id)
                )
            ]
        )

        if len(partners)==0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "DESCRIPTION": f"Partner with id {req_validation.partner_id} doesn't exist"
            }
        #SEARCH ROUTES WITH THAT MODEL
        else:
            #IF THE FLAG OF IGNORE REPEATED IS OFF, FILTER RESULTS
            if req_validation.ignored_repeated.name == False or req_validation.ignored_repeated.code == False:
                partners = partners[0]
                routes = client.env['trx_bus_traxi.routes'].search(
                    [
                        (
                            'partner.id',
                            '=',
                            partners.id
                        )
                    ]
                )
                #FILTER RESULTS BY NAME
                if not req_validation.ignored_repeated.name:
                    if req_validation.name == None:
                        req_name = ""
                    else:
                        req_name = req_validation.name
                    modified_routes = list(
                        map(
                            lambda x: "" if x.name==False else x.name,
                            list(routes)
                        )
                    )
                    by_name = list(
                        filter(
                            lambda x: x == req_name,
                            list(modified_routes)
                        )
                    )

                    if len(by_name) > 0:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        return {
                            "DESCRIPTION": f"There is already a route with the name '{req_name}' for partner {partners.id}"
                        }
                #FILTER RESULTS BY ROUTE CODE
                if not req_validation.ignored_repeated.code:
                    if req_validation.code == None:
                        req_code = ""
                    else:
                        req_code = req_validation.code
                    #print(routes[2].code)
                    modified_codes = list(
                        map(
                            lambda x: "" if x.code==False else x.code,
                            list(routes)
                        )
                    )
                    #print(modified_codes)
                    by_name = list(
                        filter(
                            lambda x: x == req_code,
                            list(modified_codes)
                        )
                    )

                    if len(by_name) > 0:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        return {
                            "DESCRIPTION": f"There is already a route with the code '{req_code}' for partner {partners.id}"
                        }


    #VALIDATE DATES
    if req_validation.init_date != None:
        init_validation = func.validate_date(req_validation.init_date ,datetime)
        if init_validation["ERROR"]:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "DESCRIPTION": f"On init_date {init_validation['DESCRIPTION']}"
            }
        else:
            init_validation = init_validation["DATE"]
    else:
        init_validation = ""

    if req_validation.end_date != None:
        end_validation = func.validate_date(req_validation.end_date ,datetime)
        if end_validation["ERROR"]:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "DESCRIPTION": f"On end_date {end_validation['DESCRIPTION']}"
            }
        else:
            end_validation = end_validation ["DATE"]
    else:
        end_validation = ""
    
    #CHECK IF END DATE IS PREVIOUS TO INIT IN WHICH CASE THAT'S AN ERROR
    if type(init_validation) == type(end_validation):
        if end_validation < init_validation:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "DESCRIPTION": f"End date {req_validation.end_date} cannot be bigger than init date {req_validation.init_date}"
            }

    
    #ONCE VALIDATED, EMPTY THE DATA IN MODEL
    #odoo_create = {}
    #ASSOCIATE STATIONS WITH ROUTE
    #odoo_create["stations"] = tuple(stations_id) if len(stations_id)>0 else False
    #NAME
    if req_validation.name == None:
        #odoo_create["name"] = False
        pass
    else:
        route_id.name  = req_validation.name

    #PARTNER ID
    if req_validation.partner_id == None:
        #route_id.partner = False
        pass
    else:
        route_id.partner = req_validation.partner_id

    #ZONE
    if req_validation.zone == None:
        #route_id.zone = False
        pass
    else: 
        route_id.zone = req_validation.zone

    #CODE
    if req_validation.code == None:
        #route_id.code = False
        pass
    else:
        route_id.code = req_validation.code

    #INIT DATE
    if init_validation =="":
        #route_id.effectiveDateSince = False
        pass
    else:
        route_id.effectiveDateSince = init_validation.strftime("%Y-%m-%d")

    #END DATE
    if end_validation=="":
        #route_id.effectiveDateUntil = False
        pass
    else:
        route_id.effectiveDateSince = end_validation.strftime("%Y-%m-%d")

    #ACTIVE
    if req_validation.available:
        route_id.availableRoute = "available"
    else:
        route_id.availableRoute = "not available"

    #THIS WON'T CREATE JUST UPDATE IN THE IFS
    #CREATE RECORD IN ODOO
    #record_id = client.env["trx_bus_traxi.routes"].create(odoo_create)
    
    #VALIDATE AND CONCENTRATE STATIONS
    if req_validation.stations == []:
        pass
    else:
        stations_id = []
        for station in req_validation.stations:
            #CREATE THOSE STATIONS
            new_station_id = client.env["trx_bus_traxi.stations"].create(
                {
                    "name": False if station.name == None else station.name,
                    "address": False if station.address == None else station.address,
                    "latitude": False if station.lat == None else station.lat,
                    "longitude": False if station.lon == None else station.lon,
                    "route_id": record_id.id
                }
            )
            stations_id.append(new_station_id.id)


    response.status_code = status.HTTP_200_OK
    return {
        "route_updated_id": route_id.id
        #"exit": 0
    }
