# models.py

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from database import Base
from datetime import datetime

class ClientMail(Base):
    __tablename__ = "client_mails"

    # A unique ID for each email record
    id = Column(Integer, primary_key=True)
    
    # The client this email belongs to (not unique anymore)
    client_id = Column(String, index=True)
    
    # Flag to check if this specific email has been marked as read
    is_read = Column(Boolean, default=False)
    
    # The date the original email was sent
    mail_date = Column(DateTime)