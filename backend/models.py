from sqlalchemy import Column, String, Boolean, DateTime, Integer
from .database import Base

class ClientMail(Base):
    __tablename__ = "client_mails"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, index=True)
    is_read = Column(Boolean, default=False)
    mail_date = Column(DateTime)
    
    # ADD THIS LINE: To store the email's unique ID and prevent duplicates
    mail_uid = Column(String, unique=True, index=True)