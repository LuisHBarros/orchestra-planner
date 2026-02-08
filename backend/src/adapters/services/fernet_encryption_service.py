"""Fernet encryption service implementation."""

from __future__ import annotations

import base64
import hashlib


class FernetEncryptionService:
    """Encryption service using Fernet symmetric crypto."""

    def __init__(self, encryption_key: str) -> None:
        if not encryption_key:
            raise RuntimeError(
                "ENCRYPTION_KEY is required when ENCRYPTION_PROVIDER != mock"
            )

        from cryptography.fernet import Fernet

        key_bytes = hashlib.sha256(encryption_key.encode("utf-8")).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        self._fernet = Fernet(fernet_key)

    async def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    async def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
