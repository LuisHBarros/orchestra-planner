"""Tests for FernetEncryptionService."""

import pytest

from backend.src.adapters.services.fernet_encryption_service import FernetEncryptionService


pytest.importorskip("cryptography")


@pytest.mark.asyncio
async def test_encrypt_decrypt_roundtrip():
    service = FernetEncryptionService("encryption-secret")

    encrypted = await service.encrypt("hello")
    decrypted = await service.decrypt(encrypted)

    assert encrypted != "hello"
    assert decrypted == "hello"
