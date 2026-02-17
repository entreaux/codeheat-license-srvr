from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv() 
from .db import init_db
from .stripe_routes import router as stripe_router
from .webhook import router as webhook_router
from .download import router as download_router
from .success_page import router as success_router

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

app.include_router(stripe_router)
app.include_router(webhook_router)
app.include_router(download_router)
app.include_router(success_router)

@app.get("/")
def root():
    return {"ok": True}
    
@app.get("/__routes")
def list_routes():
    return [route.path for route in app.routes]

@app.get("/webhook")
def webhook_get_test():
    return {"method": "GET allowed"}

