from sqlalchemy.orm import Session
from .models import ClientMail
from datetime import datetime
from collections import defaultdict

def add_mail_record(db: Session, client_id: str, mail_date: datetime, mail_uid: str, gmail_message_id: str):
    print(f"    [CRUD LOG] ADDING new mail record for UID: {mail_uid}")
    new_mail = ClientMail(
        client_id=client_id,
        mail_date=mail_date,
        is_read=False,
        mail_uid=mail_uid,
        gmail_message_id=gmail_message_id
    )
    db.add(new_mail)
    db.commit()
    return new_mail

def mark_mail_as_unread(db: Session, uid: str):
    print(f"    [CRUD LOG] MARKING mail as UNREAD for UID: {uid}")
    db.query(ClientMail).filter(ClientMail.mail_uid == uid).update({"is_read": False})
    db.commit()

def mark_client_mails_as_read(db: Session, client_id: str):
    print(f"    [CRUD LOG] MARKING ALL mail as READ for Client: {client_id}")
    db.query(ClientMail).filter(ClientMail.client_id == client_id).update({"is_read": True})
    db.commit()
    return {"status": f"All mails for client {client_id} marked as read."}

def get_client_mail_details(db: Session):
    client_details = defaultdict(lambda: {"unread_count": 0, "mails": []})
    mail_records = db.query(ClientMail).order_by(ClientMail.mail_date.desc()).all()

    for mail in mail_records:
        client_details[mail.client_id]['mails'].append({
            "is_read": mail.is_read,
            "mail_date": mail.mail_date.strftime("%Y-%m-%d %H:%M"),
            "gmail_message_id": mail.gmail_message_id
        })
        if not mail.is_read:
            client_details[mail.client_id]['unread_count'] += 1
            
    return client_details