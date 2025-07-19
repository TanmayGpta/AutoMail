from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base

# Import all models BEFORE creating tables
from models import ClientMail  # This ensures the model is registered

# Import routers AFTER models
from api.routes import router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (only once)
Base.metadata.create_all(bind=engine)

# Include router
app.include_router(router)