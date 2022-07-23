from fastapi import FastAPI
from routes import get_routes as get_routes

app = FastAPI()
app.include_router(get_routes.router)
