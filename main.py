from fastapi import FastAPI
from database import engine, Base
import models.user
import models.ward
import models.complaint
from routes import auth
from routes.complaint import router as complaint_router
from routes.health import router as health_router

app = FastAPI(title="NagarSetu API")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(complaint_router)
app.include_router(health_router)
@app.get("/")
def home():
    return {"message": "NagarSetu backend is live!"}

@app.get("/health")
def health():
    return {"status": "ok", "db": "connected"}