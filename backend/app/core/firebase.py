import firebase_admin
from firebase_admin import credentials
from app.config import settings
import os

_firebase_app = None


def get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        storage_config = {"storageBucket": settings.FIREBASE_STORAGE_BUCKET}
        cred_path = settings.FIREBASE_CREDENTIALS_PATH

        try:
            _firebase_app = firebase_admin.get_app()
        except ValueError:
            if os.path.exists(cred_path):
                # 로컬: 서비스 계정 JSON 파일 사용
                cred = credentials.Certificate(cred_path)
                _firebase_app = firebase_admin.initialize_app(cred, storage_config)
            else:
                # Cloud Run: Application Default Credentials 사용
                cred = credentials.ApplicationDefault()
                _firebase_app = firebase_admin.initialize_app(cred, storage_config)
    return _firebase_app
