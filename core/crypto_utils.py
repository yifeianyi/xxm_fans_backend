import base64
import os
from cryptography.fernet import Fernet
from django.conf import settings


def _get_fernet():
    key = getattr(settings, 'FERNET_KEY', None)
    if not key:
        secret = getattr(settings, 'SECRET_KEY', '')
        key = base64.urlsafe_b64encode(secret.encode()[:32].ljust(32, b'\0'))
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _get_fernet().decrypt(ciphertext.encode()).decode()
