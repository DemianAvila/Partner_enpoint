from odooly import Client
from fastapi import FastAPI, Request


app = FastAPI()

# MUST CHANGE TO THE ENV FILE
client = Client(server = "http://localhost:8069", 
    db = "trx_business", 
    user = "admin", 
    password = "admin"
)

@app.get('/get_routes')
async def get_routes(request: Request):
    #TRY TO GET THE REQUEST BODY
    try:
        req = await request.json()
    except Exception as e:
        return {
            "STATUS": 408,
            "DESCRIPTION": "Timeout, could not get the request",
            "EXCEPTION": str(e)
        }
    #VALIDATE THE REQUEST
    accepted_parameters = ['filters', 'order_by', 'accept']
    for key in req.keys():
        if key not in accepted_parameters:
            return {
                "STATUS": 404,
                "DESCRIPTION": f"{key} is not accepted in this request"
            }
    #TRY TO READ THE ODOO ROUTE'S MODEL
    try:        
        routes = client.env['trx_bus_traxi.routes'].search([])
    except Exception as e:
        return {
            "STATUS": 408,
            "DESCRIPTION": "Timeout, no connection to database",
            "EXCEPTION": str(e)
        }

    response = {
        "STATUS": 200,
        "DESCRIPTION": "OK",
        "routes":[]
    }

    for route in routes:
        response['routes'].append({
                "name": route.name
            }
        )
    return response

