from fastapi import FastAPI
from app.routers import temperature, version

app = FastAPI()
app.include_router(version.router)
app.include_router(temperature.router)
