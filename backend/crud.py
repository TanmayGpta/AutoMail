from sqlalchemy.orm import Session
from models import ClientMailStatus
from datetime import datetime

def upsert_client_status(db: Session, client_id: str):
    record = db.query(ClientMailStatus).filter_by(client_id=client_id).first()
    if record:
        record.unread = True
        record.last_updated = datetime.utcnow()
    else:
        record = ClientMailStatus(client_id=client_id)
        db.add(record)
    db.commit()
    return record

def get_unread_clients(db: Session):
    return db.query(ClientMailStatus).filter_by(unread=True).all()

def mark_as_read(db: Session, client_id: str):
    record = db.query(ClientMailStatus).filter_by(client_id=client_id).first()
    if record:
        record.unread = False
        db.commit()
