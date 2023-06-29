# credentials.py

from app.config.config import Settings

app_settings = Settings()

firebase_credentials = {
    "type": "service_account",
    "project_id": app_settings.FIREBASE_PROJECT_ID,
    "private_key_id": app_settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": app_settings.FIREBASE_PRIVATE_KEY,
    "client_email": app_settings.FIREBASE_CLIENT_EMAIL,
    "client_id": app_settings.FIREBASE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ktimd%40react-native-fiufit.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}
