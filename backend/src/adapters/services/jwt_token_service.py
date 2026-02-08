"""JWT token service implementation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from backend.src.config.settings import AppSettings
from backend.src.domain.ports.services import RevokedTokenStore, TokenPair


class JWTTokenService:
    """Token service backed by signed JWTs."""

    def __init__(
        self,
        settings: AppSettings,
        revoked_token_store: RevokedTokenStore,
    ) -> None:
        if not settings.jwt_secret_key:
            raise RuntimeError("JWT_SECRET_KEY is required when TOKEN_PROVIDER != mock")

        self._secret = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_exp_minutes = settings.access_token_expiry_minutes
        self._refresh_exp_minutes = settings.refresh_token_expiry_minutes
        self._revoked_token_store = revoked_token_store

    def _jwt(self):
        import jwt

        return jwt

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _encode(self, payload: dict[str, Any]) -> str:
        return self._jwt().encode(payload, self._secret, algorithm=self._algorithm)

    async def _decode(self, token: str) -> dict[str, Any] | None:
        try:
            payload = self._jwt().decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
            )
        except Exception:
            return None

        jti = payload.get("jti")
        if isinstance(jti, str) and await self._revoked_token_store.is_revoked(jti):
            return None
        return payload

    async def _revoke_payload_jti(self, payload: dict[str, Any]) -> None:
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not isinstance(jti, str) or not isinstance(exp, int):
            return

        ttl_seconds = max(1, exp - int(self._now().timestamp()))
        await self._revoked_token_store.revoke(jti, ttl_seconds)

    async def generate_tokens(
        self,
        user_id: UUID,
        claims: dict[str, Any] | None = None,
    ) -> TokenPair:
        now = self._now()
        base_claims = claims or {}

        access_payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._access_exp_minutes)).timestamp()),
            "jti": str(uuid4()),
            **base_claims,
        }
        refresh_payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._refresh_exp_minutes)).timestamp()),
            "jti": str(uuid4()),
            **base_claims,
        }

        return TokenPair(
            access_token=self._encode(access_payload),
            refresh_token=self._encode(refresh_payload),
        )

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        payload = await self._decode(token)
        if not payload or payload.get("type") != "access":
            return None
        return payload

    async def refresh_token(self, token: str) -> TokenPair | None:
        payload = await self._decode(token)
        if not payload or payload.get("type") != "refresh":
            return None

        await self._revoke_payload_jti(payload)

        user_id = payload.get("user_id")
        if not user_id:
            return None

        try:
            uid = UUID(str(user_id))
        except ValueError:
            return None

        claims = {
            k: v
            for k, v in payload.items()
            if k not in {"sub", "user_id", "type", "iat", "exp", "jti"}
        }
        return await self.generate_tokens(uid, claims)

    async def revoke_token(self, token: str) -> dict[str, Any] | None:
        payload = await self._decode(token)
        if not payload:
            return None

        await self._revoke_payload_jti(payload)
        return payload
