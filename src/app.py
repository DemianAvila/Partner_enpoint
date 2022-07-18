from odooly import Client
from fastapi import FastAPI, Request, Response, status


app = FastAPI()

# MUST CHANGE TO THE ENV FILE
client = Client(server = "http://localhost:8069", 
    db = "trx_business", 
    user = "admin", 
    password = "admin"
)



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
    #VALIDATE THE REQUEST
    accepted_parameters = ['filters', 'order_by', 'accept']
    accepted_filters = ['route_name', 'route_id', 'partner_name', 'parter_id',
            'available', 'active']
    order_by_params = ['name', 'zone', 'code', 'distance', 'partner', 
            'start_date', 'end_date']
    accept_search = ['case_sensitive', 'reg_exp']
    for key in req.keys():
        if key not in accepted_parameters:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "DESCRIPTION": f"'{key}' is not accepted in this request"
            }
        else:
            if key == 'filters':
                if str(type(req[key])) != '<class \'dict\'>':
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {
                        "DESCRIPTION": f"'{key}' must be object"
                    }
                for subkey in req[key].keys():
                    if subkey not in accepted_filters:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {
                            "DESCRIPTION": f"Subkey '{subkey}' not accepted in '{key}'"
                        }
            elif key == 'order_by':
                if str(type(req[key])) != '<class \'dict\'>':
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {
                        "DESCRIPTION": f"'{key}' must be object"
                    }
                for subkey in req[key].keys():
                    if subkey not in order_by_params:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {
                            "DESCRIPTION": f"Subkey '{subkey}' not accepted in '{key}'"
                        }
            elif key == 'accept':
                if str(type(req[key])) != '<class \'dict\'>':
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return {
                        "DESCRIPTION": f"'{key}' must be object"
                    }
                for subkey in req[key].keys():
                    if subkey not in accept_search:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {
                            "DESCRIPTION": f"Subkey '{subkey}' not accepted in '{key}'"
                        }

    #TRY TO READ THE ODOO ROUTE'S MODEL
    try:        
        routes = client.env['trx_bus_traxi.routes'].search([])
    except Exception as e:
        response.status_code = status.HTTP_408_REQUEST_TIMEOUT
        return {
            "DESCRIPTION": "Timeout, no connection to database",
            "EXCEPTION": str(e)
        }
    
    response.status_code = status.HTTP_200_OK
    resp = {
        "DESCRIPTION": "OK",
        "routes":[]
    }

    for route in routes:
        resp['routes'].append({
                "name": route.name
            }
        )
    return resp

