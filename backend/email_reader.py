# email_reader.py

from imap_tools import MailBox, AND
import pytesseract
from PIL import Image
import io, os, zipfile
from crud import add_mail_record
from database import SessionLocal
import re
from client_loader import load_clients


# 🔹 If PATH didn't work, set this:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

EMAIL = "predecentt@gmail.com"
PASSWORD = "xzql nrao yrwe wvys"
IMAP_SERVER = "imap.gmail.com"

# 🔸 Replace this with real list or fetch from DB later
approved_ids = [row["Client ID"] for row in load_clients()]

def extract_client_id(text, approved_ids):
    for cid in approved_ids:
        # Matches whole word (not part of another word)
        if re.search(rf"\b{cid}\b", text):
            return cid
    return None

def process_emails():
    print("🚀 Starting client email processor...")
    db = SessionLocal()
    os.makedirs("client_docs", exist_ok=True)

    with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
        print("📬 Logged into mailbox successfully.")

        mails = list(mailbox.fetch(criteria=AND(seen=False, subject='Client Info Update'), mark_seen=False))
        print(f"📨 Found {len(mails)} unread matching emails.")

        for msg in mails:
            print(f"🔍 Processing email: {msg.subject} from {msg.from_}")
            client_id = None

            for att in msg.attachments:
                if att.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    img = Image.open(io.BytesIO(att.payload))
                    text = pytesseract.image_to_string(img)

                    client_id = extract_client_id(text, approved_ids)
                    if client_id:
                        break  # stop after finding a match

            if not client_id:
                continue  # skip this email if no match found

            # 🗂️ Save all attachments into a zip named by client_id
            zip_path = f"client_docs/{client_id}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for att in msg.attachments:
                    zf.writestr(att.filename, att.payload)

            # ✅ Add a new record for this mail in the DB
            add_mail_record(db, client_id, msg.date)
            print(f"✅ Logged new mail for client {client_id} on {msg.date.strftime('%Y-%m-%d')}")


    db.close()


if __name__ == "__main__":
    print("🚀 Starting client email processor...")
    process_emails()