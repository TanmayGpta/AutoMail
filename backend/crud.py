from sqlalchemy.orm import Session
from sqlalchemy import func, case
from .models import ClientMail
from datetime import datetime
from typing import List # <-- Add this import

def add_mail_record(db: Session, client_id: str, mail_date: datetime, mail_uid: str):
    # ... (this function is unchanged)
    new_mail = ClientMail(
        client_id=client_id,
        mail_date=mail_date,
        is_read=False,
        mail_uid=mail_uid
    )
    db.add(new_mail)
    db.commit()
    return new_mail

def mark_specific_mails_as_read(db: Session, uids: List[str]): # <-- ADD THIS NEW FUNCTION
    """Marks a specific list of emails as read based on their UIDs."""
    if not uids:
        return
    db.query(ClientMail).filter(ClientMail.mail_uid.in_(uids)).update({"is_read": True}, synchronize_session=False)
    db.commit()
    print(f"    [SYNC] Synced {len(uids)} mail(s) to 'Read' status from Gmail.")

def mark_mail_as_unread(db: Session, uid: str): # <-- ADD THIS NEW FUNCTION
    """Marks a single email as unread based on its UID."""
    db.query(ClientMail).filter(ClientMail.mail_uid == uid).update({"is_read": False})
    db.commit()
    
def mark_client_mails_as_read(db: Session, client_id: str):
    # ... (this function is unchanged)
    db.query(ClientMail).filter(ClientMail.client_id == client_id).update({"is_read": True})
    db.commit()
    return {"status": f"All mails for client {client_id} marked as read."}

def get_mail_statuses(db: Session):
    results = (
        db.query(
            ClientMail.client_id,
            func.sum(case((ClientMail.is_read == False, 1)), else_=0).label("unread_count"),
            func.max(ClientMail.mail_date).label("latest_mail_date"),
        )
        .group_by(ClientMail.client_id)
        .all()
    )
    status_map = {
        row.client_id: {
            "unread_count": row.unread_count,
            "mail_date": row.latest_mail_date.strftime("%Y-%m-%d %H:%M") if row.latest_mail_date else None,
        }
        for row in results
    }
    return status_map