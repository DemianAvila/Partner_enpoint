from fastapi import FastAPI
from routes import get_routes as get_routes
from routes import post_routes as post_routes

app = FastAPI()
app.include_router(get_routes.router)
app.include_router(post_routes.router)

