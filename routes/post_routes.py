from .models import  post_routes_models as post_models
from odooly import Client
from fastapi import APIRouter, Request, Response, status, Depends
from pydantic import ValidationError
from datetime import datetime, date

router = APIRouter(tags=["Routes"])

client = Client(server = "http://localhost:8069",                                     
    db = "trx_business",                                                              
    user = "admin",                                                                   
    password = "admin"                                                                
)

@router.post('/post_route')
async def post_routes(request: Request,                                                
    response: Response,                                                               
    commons: post_models.PostRoute = Depends()):
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
        req_validation = post_models.PostRoute(**req)                     
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


        
    print(req_validation)    
    response.status_code = status.HTTP_200_OK
    return {
        "exit_status": 0
        }
