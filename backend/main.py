from fastapi import FastAPI
from api.routes import router
from models import Base
from database import engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
Base.metadata.create_all(bind=engine)  