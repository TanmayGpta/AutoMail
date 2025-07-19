import os
import sys
import time
import re
import io
import zipfile
import pytz
from datetime import datetime
from PIL import Image
import pytesseract
from imap_tools import MailBox, AND

from .database import SessionLocal
from .crud import add_mail_record, mark_specific_mails_as_read, mark_mail_as_unread
from .client_loader import load_clients
from .models import ClientMail

# --- Your settings ---
EMAIL = os.getenv("GMAIL_USER", "predecentt@gmail.com")
PASSWORD = os.getenv("GMAIL_PASSWORD", "xzql nrao yrwe wvys")
IMAP_SERVER = "imap.gmail.com"
# ... (rest of settings are the same) ...

def main_loop():
    print("🕵️  Running in DIAGNOSTIC MODE. This will only run once.")
    
    db = SessionLocal()
    try:
        with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
            
            print("--- DIAGNOSTIC: Fetching all emails with subject 'Client Info Update' ---")
            
            # Temporarily fetch all emails matching the subject, ignoring the read/unread status
            messages_from_gmail = list(mailbox.fetch(criteria=AND(subject='Client Info Update'), mark_seen=False))
            
            print(f"\nFound {len(messages_from_gmail)} total message(s) with that subject.")
            print("Here are their flags (if '\\Seen' is present, the server considers it READ):\n")

            for msg in messages_from_gmail:
                # Print the UID and the flags for each message
                print(f"  - UID: {msg.uid}, Flags: {msg.flags}")

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        db.close()

# This makes the script runnable
if __name__ == "__main__":
    main_loop()