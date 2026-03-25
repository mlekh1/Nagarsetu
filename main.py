from fastapi import FastAPI
from database import engine, Base
import models.user
import models.ward
import models.complaint
from routes import auth
from routes.complaint import router as complaint_router
from routes.health import router as health_router
from fastapi.middleware.cors import CORSMiddleware
from routes.admin import router as admin_router

app = FastAPI(title="NagarSetu API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(complaint_router)
app.include_router(health_router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {"message": "NagarSetu backend is live!"}

@app.get("/health")
def health():
    return {"status": "ok", "db": "connected"}