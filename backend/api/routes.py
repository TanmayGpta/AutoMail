from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from crud import get_unread_clients, mark_as_read
from database import SessionLocal
from fastapi.responses import FileResponse
from client_loader import load_clients
from typing import Optional
import os
from models import ClientMailStatus  # ⬅️ This is required!

router = APIRouter()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔴 Get all unread client IDs (used internally or directly)
@router.get("/unread-mails")
def unread_clients(db: Session = Depends(get_db)):
    return get_unread_clients(db)

# ✅ Mark a single client as read
@router.post("/mark-read/{client_id}")
def mark_read(client_id: str, db: Session = Depends(get_db)):
    mark_as_read(db, client_id)
    return {"status": "marked as read"}

# 📥 Download the .zip file for that client
@router.get("/download/{client_id}")
def download_zip(client_id: str):
    zip_path = f"client_docs/{client_id}.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=zip_path, filename=f"{client_id}.zip", media_type='application/zip')

# 📊 Full client table (merged from Excel + DB)
@router.get("/clients")
def get_clients(
    branch: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    all_clients = load_clients()

    # Fetch all mail status rows
    status_rows = db.query(ClientMailStatus).all()
    status_map = {
        row.client_id: {
            "unread": row.unread,
            "mail_date": row.mail_date.strftime("%Y-%m-%d %H:%M") if row.mail_date else None
        }
        for row in status_rows
    }

    enriched_clients = []
    for client in all_clients:
        cid = client.get("Client ID", "")
        name = client.get("ClientName", "")
        branch_name = client.get("Branch Name", "")

        zip_path = f"client_docs/{cid}.zip"
        zip_exists = os.path.exists(zip_path)

        status_info = status_map.get(cid)

        if status_info:
            if status_info["unread"]:
                status = "Unread"
            else:
                status = "Read"
            mail_date = status_info["mail_date"]
        else:
            status = "No new mails"
            mail_date = None

        enriched_clients.append({
            "Client ID": cid,
            "Client Name": name,
            "Branch Name": branch_name,
            "status": status,
            "mail_date": mail_date,
            "zip_available": zip_exists
        })

    if branch:
        enriched_clients = [c for c in enriched_clients if c["Branch Name"] == branch]

    return enriched_clients