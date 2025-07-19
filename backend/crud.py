# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models import ClientMail # Import the new ClientMail model
from datetime import datetime

def add_mail_record(db: Session, client_id: str, mail_date: datetime):
    """Adds a new, unread mail record to the database."""
    new_mail = ClientMail(
        client_id=client_id,
        mail_date=mail_date,
        is_read=False # A new mail is always unread by default
    )
    db.add(new_mail)
    db.commit()
    return new_mail

def mark_client_mails_as_read(db: Session, client_id: str):
    """Marks ALL mail for a given client_id as read."""
    db.query(ClientMail).filter(ClientMail.client_id == client_id).update({"is_read": True})
    db.commit()
    return {"status": f"All mails for client {client_id} marked as read."}

def get_mail_statuses(db: Session):
    """
    Gets the unread mail count and latest mail date for all clients.
    This uses one efficient query to get all data at once.
    """
    results = (
        db.query(
            ClientMail.client_id,
            func.sum(case((ClientMail.is_read == False, 1)), else_=0).label("unread_count"),
            func.max(ClientMail.mail_date).label("latest_mail_date"),
        )
        .group_by(ClientMail.client_id)
        .all()
    )

    # Convert the list of results into a dictionary for fast lookups
    status_map = {
        row.client_id: {
            "unread_count": row.unread_count,
            "mail_date": row.latest_mail_date.strftime("%Y-%m-%d %H:%M") if row.latest_mail_date else None,
        }
        for row in results
    }
    return status_map