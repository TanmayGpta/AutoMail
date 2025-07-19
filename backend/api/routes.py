# routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..crud import get_mail_statuses, mark_client_mails_as_read
from ..database import SessionLocal
from fastapi.responses import FileResponse
from ..client_loader import load_clients
from typing import Optional
import os

router = APIRouter()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Mark ALL of a single client's mails as read
@router.post("/mark-read/{client_id}")
def mark_read(client_id: str, db: Session = Depends(get_db)):
    mark_client_mails_as_read(db, client_id)
    return {"status": "marked as read"}

# 📥 Download the .zip file for that client
@router.get("/download/{client_id}")
def download_zip(client_id: str):
    zip_path = f"client_docs/{client_id}.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=zip_path, filename=f"{client_id}.zip", media_type='application/zip')

# 📊 Full client table (merged from Excel + DB with counts)
@router.get("/clients")
def get_clients(
    branch: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    all_clients = load_clients()
    
    # Get the map of { client_id: { unread_count: X, mail_date: Y } }
    status_map = get_mail_statuses(db)

    enriched_clients = []
    for client in all_clients:
        cid = client.get("Client ID", "")
        status_info = status_map.get(cid)

        # New logic for determining status based on count
        unread_count = 0
        mail_date = None
        if status_info:
            unread_count = status_info.get("unread_count", 0)
            mail_date = status_info.get("mail_date")

        enriched_clients.append({
            "Client ID": cid,
            "Client Name": client.get("ClientName", ""),
            "Branch Name": client.get("Branch Name", ""),
            "unread_count": unread_count,
            "mail_date": mail_date,
        })

    if branch:
        enriched_clients = [c for c in enriched_clients if c["Branch Name"] == branch]

    return enriched_clients