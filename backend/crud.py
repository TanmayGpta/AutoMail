from sqlalchemy.orm import Session
from models import ClientMailStatus
from datetime import datetime

def upsert_client_status(db, client_id, mail_date=None):
    existing = db.query(ClientMailStatus).filter_by(client_id=client_id).first()

    if existing:
        existing.unread = True  # ✅ Explicitly mark unread
        existing.last_updated = datetime.utcnow()
        if mail_date:
            existing.mail_date = mail_date
    else:
        new_entry = ClientMailStatus(
            client_id=client_id,
            unread=True,  # ✅ Important!
            mail_date=mail_date,
            last_updated=datetime.utcnow()
        )
        db.add(new_entry)

    db.commit()
