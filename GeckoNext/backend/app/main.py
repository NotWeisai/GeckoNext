from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.routers import auth, tasks
from app.database import engine
from app.models import Base

app = FastAPI(title="Gecko Next API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Gecko Next Backend работает!"}