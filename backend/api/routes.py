# routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..crud import get_client_mail_details, mark_client_mails_as_read
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
def get_clients(branch: Optional[str] = Query(None), db: Session = Depends(get_db)):
    all_clients_from_file = load_clients()
    mail_details_from_db = get_client_mail_details(db)

    enriched_clients = []
    for client in all_clients_from_file:
        cid = client.get("Client ID", "")
        details = mail_details_from_db.get(cid, {"unread_count": 0, "mails": []})

        enriched_clients.append({
            "Client ID": cid,
            "Client Name": client.get("ClientName", ""),
            "Branch Name": client.get("Branch Name", ""),
            "unread_count": details['unread_count'],
            "mails": details['mails'] # Pass the full list of mails
        })

    if branch:
        enriched_clients = [c for c in enriched_clients if c["Branch Name"] == branch]

    return enriched_clients