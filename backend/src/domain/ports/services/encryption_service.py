"""Encryption service port."""

from typing import Protocol


class EncryptionService(Protocol):
    """Port for encryption operations.

    BR-LLM-002: API Keys must be stored encrypted.
    """

    async def encrypt(self, plaintext: str) -> str: ...

    async def decrypt(self, ciphertext: str) -> str: ...
