# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ update this if your DB path is different
SQLALCHEMY_DATABASE_URL = "sqlite:///./clients.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

# ⛔ TEMPORARY: Drop and recreate the tables

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
