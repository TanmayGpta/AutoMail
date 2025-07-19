# backend/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get the absolute path to the directory where this file (database.py) is located.
# This will always be the 'backend' directory.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the full path for the database file inside the 'backend' directory.
DB_PATH = os.path.join(BACKEND_DIR, "clients.db")

# The f"sqlite:///{DB_PATH}" ensures we always use the same file.
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"✅ Using database at: {SQLALCHEMY_DATABASE_URL}") # Helpful debug print

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()