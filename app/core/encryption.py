from cryptography.fernet import Fernet
import base64
import hashlib
import os
from typing import Optional


class DataEncryption:
    """Шифрование ПД и хеширование email"""

    def __init__(self):
        secret_key = os.getenv('ENCRYPTION_KEY', 'stroimagencryptkey')
        key_bytes = hashlib.sha256(secret_key.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt(self, data: str) -> str:
        if data is None:
            return None
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode('utf-8')

    def decrypt(self, encrypted_data: str) -> Optional[str]:
        if encrypted_data is None:
            return None
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return decrypted.decode('utf-8')
        except Exception:
            return None

    def hash_email(self, email: str) -> str:
        if not email:
            return None
        normalized_email = email.lower().strip()
        return hashlib.sha256(normalized_email.encode()).hexdigest()


encryption_service = DataEncryption()
