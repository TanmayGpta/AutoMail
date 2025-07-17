from sqlalchemy import Column, String, Boolean, DateTime
from database import Base
from datetime import datetime

class ClientMailStatus(Base):
    __tablename__ = "client_mail_status"
    client_id = Column(String, primary_key=True, index=True)
    unread = Column(Boolean, default=True)
    mail_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
