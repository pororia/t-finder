from cryptography.fernet import Fernet
from app.config import settings
import base64


def _get_fernet() -> Fernet:
    key = settings.PASSWORD_ENCRYPTION_KEY
    if not key:
        key = base64.urlsafe_b64encode(b"dev_key_32_bytes_padding_here!!").decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_password(plain_text: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    try:
        f = _get_fernet()
        return f.decrypt(encrypted.encode()).decode()
    except Exception:
        return "****"
