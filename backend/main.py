from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes

app = FastAPI(title="AutoMail API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes
app.include_router(routes.router)

@app.get("/", tags=["Default"])
def read_root():
    return {"message": "Welcome to the AutoMail API"}