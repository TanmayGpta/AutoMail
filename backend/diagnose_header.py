import os
from imap_tools import MailBox, AND

# --- Your settings ---
EMAIL = os.getenv("GMAIL_USER", "predecentt@gmail.com")
PASSWORD = os.getenv("GMAIL_PASSWORD", "xzql nrao yrwe wvys")
IMAP_SERVER = "imap.gmail.com"

def run_diagnostic():
    print("🕵️  Running Diagnostic: Fetching headers for unread emails...")
    try:
        with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
            
            # Find all unread emails with the correct subject
            unread_messages = list(mailbox.fetch(criteria=AND(seen=False, subject='Client Info Update')))
            
            if not unread_messages:
                print("\nNo unread emails with subject 'Client Info Update' were found.")
                return

            print(f"\nFound {len(unread_messages)} unread message(s). Here are their details:")
            
            for msg in unread_messages:
                # Print the UID and the raw header for each message
                print(f"\n--- Details for UID: {msg.uid} ---")
                raw_header = msg.headers.get('message-id', ['!!! HEADER IS MISSING !!!'])[0]
                
                # The !r prints the string with quotes and escape characters so we can see its exact structure
                print(f"Raw Message-ID Header: {raw_header!r}") 

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    run_diagnostic()