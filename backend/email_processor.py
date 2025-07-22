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
from .crud import add_mail_record, mark_mail_as_unread
from .client_loader import load_clients
from .models import ClientMail

# --- Your settings ---
EMAIL = os.getenv("GMAIL_USER", "predecentt@gmail.com")
PASSWORD = os.getenv("GMAIL_PASSWORD", "xzql nrao yrwe wvys")
IMAP_SERVER = "imap.gmail.com" # <-- THIS IS THE FIX
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_client_id(text, approved_ids):
    for cid in approved_ids:
        if re.search(rf"\b{cid}\b", text):
            return cid
    return None

def main_loop():
    print("📧 Email checker script started. Syncing every 2 minutes.")
    approved_ids = [row["Client ID"] for row in load_clients()]

    while True:
        print("\n---------------------------------")
        print(f"[{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p')}] Running sync cycle...")
        db = SessionLocal()
        try:
            with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
                
                all_mails_in_db = {mail.mail_uid: mail for mail in db.query(ClientMail).all()}
                print(f"  [DEBUG] DB knows about {len(all_mails_in_db)} mail(s) total.")

                # Perform one "safe" fetch to get all unread messages with clean headers
                unread_messages = list(mailbox.fetch(criteria=AND(seen=False, subject='Client Info Update'), mark_seen=False))
                print(f"  [INFO] Found {len(unread_messages)} unread mail(s) in Gmail.")

                for msg in unread_messages:
                    # Case A: Brand new email
                    if msg.uid not in all_mails_in_db:
                        print(f"  -> Processing NEW mail with UID: {msg.uid}")

                        # FIRST, get the clean Message-ID from this initial, safe fetch
                        message_id_header = msg.headers.get('message-id', ['<>'])[0]
                        message_id = message_id_header.strip().strip('<>')
                        
                        client_id = None
                        for att in msg.attachments:
                            if att.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                                try:
                                    img = Image.open(io.BytesIO(att.payload))
                                    text = pytesseract.image_to_string(img)
                                    client_id = extract_client_id(text, approved_ids)
                                    if client_id: break
                                except Exception as e:
                                    print(f"    [ERROR] Could not process image {att.filename}: {e}")
                        
                        if client_id:
                            print(f"    [SUCCESS] Found Client ID: {client_id}. Saving and logging.")
                            zip_path = f"client_docs/{client_id}.zip"
                            os.makedirs("client_docs", exist_ok=True)
                            with zipfile.ZipFile(zip_path, 'w') as zf:
                                for att in msg.attachments:
                                    zf.writestr(att.filename, att.payload)
                            
                            add_mail_record(db, client_id, msg.date, msg.uid, message_id)
                        else:
                            # This is the new logic for the email with text in the body
                            print("    [INFO] No image attachment found. Checking email body for Client ID...")
                            client_id_from_body = extract_client_id(msg.text, approved_ids)
                            if client_id_from_body:
                                print(f"    [SUCCESS] Found Client ID in body: {client_id_from_body}. Logging.")
                                add_mail_record(db, client_id_from_body, msg.date, msg.uid, message_id)
                            else:
                                print(f"    [INFO] No valid Client ID found in this email.")

                    # Case B: Old email that was marked as unread again
                    else:
                        if all_mails_in_db[msg.uid].is_read:
                            print(f"  -> Syncing EXISTING mail with UID: {msg.uid} to UNREAD.")
                            mark_mail_as_unread(db, msg.uid)

        except Exception as e:
            print(f"[ERROR] An unhandled error occurred: {e}")
        finally:
            db.close()
        
        print("Cycle complete. Waiting 2 minutes.")
        time.sleep(120)

if __name__ == "__main__":
    main_loop()