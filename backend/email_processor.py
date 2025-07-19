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
        print("---------------------------------")
        print(f"[{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p')}] Running sync cycle...")
        db = SessionLocal()
        try:
            with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
                
                # Step 1: Get the complete, true list of unread UIDs from Gmail. This is our source of truth.
                live_unread_uids = {msg.uid for msg in mailbox.fetch(criteria=AND(seen=False, subject='Client Info Update'), mark_seen=False)}
                print(f"  [INFO] Gmail reports {len(live_unread_uids)} unread mail(s) with matching subject.")

                # Step 2: Get the state of our application's database.
                all_mails_in_db = {mail.mail_uid: mail for mail in db.query(ClientMail).all()}
                unread_uids_in_db = {uid for uid, mail in all_mails_in_db.items() if not mail.is_read}

                # Step 3: Reconcile the states.

                # A) Find emails that must be marked as READ in our app.
                # These are emails that our app thinks are unread, but are NOT in the live unread list from Gmail.
                uids_to_mark_as_read = unread_uids_in_db - live_unread_uids
                if uids_to_mark_as_read:
                    print(f"  [SYNC] Found {len(uids_to_mark_as_read)} mail(s) read by user in Gmail. Syncing to app.")
                    mark_specific_mails_as_read(db, list(uids_to_mark_as_read))
                
                # B) Find emails that must be marked as UNREAD or ADDED to our app.
                for uid in live_unread_uids:
                    # Case 1: It's a brand new email we have never processed.
                    if uid not in all_mails_in_db:
                        # We need to fetch the full message details for this new email
                        for msg in mailbox.fetch(AND(uid=uid)):
                            print(f"  -> Found new mail (UID: {msg.uid}) from {msg.from_}")
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
                                add_mail_record(db, client_id, msg.date, msg.uid)
                            else:
                                print("    [INFO] No valid Client ID found. Skipping.")

                    # Case 2: It's an old email that was marked as UNREAD again.
                    else:
                        if all_mails_in_db[uid].is_read:
                            print(f"  -> [SYNC] Found old mail (UID: {uid}) re-marked as unread in Gmail. Syncing.")
                            mark_mail_as_unread(db, uid)

        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
        finally:
            db.close()
        
        print("Cycle complete. Waiting 2 minutes.")
        time.sleep(120)

if __name__ == "__main__":
    main_loop()