import os
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    def __init__(self):
        # Telegram tokens
        self.REMINDER_BOT_TOKEN = os.getenv("REMINDER_BOT_TOKEN")
        self.DOCS_BOT_TOKEN = os.getenv("DOCS_BOT_TOKEN")
        
        # Google Docs configuration
        self.GOOGLE_DOC_ID = os.getenv("GOOGLE_DOC_ID")
        
        # Properly format the service account info
        self.GOOGLE_SERVICE_ACCOUNT = {
            "type": "service_account",
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
        }
