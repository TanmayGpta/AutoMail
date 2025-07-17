from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import get_unread_clients, mark_as_read
from database import SessionLocal
from fastapi.responses import FileResponse
from typing import Optional
from fastapi import Query

import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/unread-mails")
def unread_clients(db: Session = Depends(get_db)):
    return get_unread_clients(db)

@router.post("/mark-read/{client_id}")
def mark_read(client_id: str, db: Session = Depends(get_db)):
    mark_as_read(db, client_id)
    return {"status": "marked as read"}

@router.get("/download/{client_id}")
def download_zip(client_id: str):
    zip_path = f"client_docs/{client_id}.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=zip_path, filename=f"{client_id}.zip", media_type='application/zip')
