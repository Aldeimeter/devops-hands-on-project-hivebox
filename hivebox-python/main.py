from fastapi import FastAPI
from app.routers import version

app = FastAPI()
app.include_router(version.router)
