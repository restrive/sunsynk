"""Async Sunsynk Cloud API client."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

try:  # pragma: no cover - fallback for test environments without aiohttp
    from aiohttp import ClientSession, ClientError
except ImportError:  # pragma: no cover
    ClientSession = Any  # type: ignore[misc, assignment]
    ClientError = Exception
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .const import (
    DEFAULT_BASE_URL,
    DEFAULT_LAN,
    DEFAULT_SOURCE,
    FLOW_ENDPOINT,
    GEN_USE_ENDPOINT,
    INVERTER_COUNT_ENDPOINT,
    INVERTER_SUMMARY_ENDPOINT,
    MESSAGE_COUNT_ENDPOINT,
    PLANT_REALTIME_ENDPOINT,
    PLANT_SUMMARY_ENDPOINT,
    REALTIME_ENDPOINT,
    WEATHER_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)

LEGACY_REALTIME_ENDPOINTS: dict[str, dict[str, Any]] = {
    "battery": {
        "path": "/api/v1/inverter/battery/{sn}/realtime",
        "params": {"sn": "{sn}", "lan": "{lan}"},
    },
    "grid": {
        "path": "/api/v1/inverter/grid/{sn}/realtime",
        "params": {"sn": "{sn}"},
    },
    "load": {
        "path": "/api/v1/inverter/load/{sn}/realtime",
        "params": {},
    },
}


class SunsynkApiError(RuntimeError):
    """Raised when Sunsynk API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        payload: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.payload = payload or {}


class SunsynkApiClient:
    """Helper for interacting with Sunsynk APIs."""

    def __init__(
        self,
        session: ClientSession,
        *,
        email: str,
        password: str,
        plant_id: str,
        inverter_sn: str,
        lan: str = DEFAULT_LAN,
        source: str = DEFAULT_SOURCE,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self._session = session
        self._email = email
        self._password = password
        self._plant_id = plant_id
        self._inverter_sn = inverter_sn
        self._lan = lan
        self._source = source
        self._base_url = base_url.rstrip("/")

        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._token_lock = asyncio.Lock()

    # -------------------------------------------------------------------------
    # Public API helpers
    # -------------------------------------------------------------------------

    async def async_get_flow(self) -> dict[str, Any]:
        return await self._authenticated_get(
            FLOW_ENDPOINT.format(sn=self._inverter_sn)
        )

    async def async_get_inverter_realtime(self, category: str) -> dict[str, Any]:
        override = LEGACY_REALTIME_ENDPOINTS.get(category)
        if override:
            path = override["path"].format(sn=self._inverter_sn)
            params = self._format_params(override.get("params"))
            _LOGGER.debug(
                "Using legacy realtime endpoint for category '%s': %s",
                category,
                override["path"],
            )
            return await self._authenticated_get(path, params=params)

        return await self._authenticated_get(
            REALTIME_ENDPOINT.format(sn=self._inverter_sn, category=category)
        )

    async def async_get_plant_realtime(self) -> dict[str, Any]:
        path = PLANT_REALTIME_ENDPOINT.format(plant_id=self._plant_id)
        return await self._authenticated_get(path)

    async def async_get_plant_summary(self) -> dict[str, Any]:
        path = PLANT_SUMMARY_ENDPOINT.format(plant_id=self._plant_id)
        return await self._authenticated_get(path, params={"lan": self._lan})

    async def async_get_weather(self, lon_lat: str) -> dict[str, Any]:
        return await self._authenticated_get(
            WEATHER_ENDPOINT,
            params={"lan": self._lan, "lonLat": lon_lat},
        )

    async def async_get_message_count(self) -> dict[str, Any]:
        return await self._authenticated_get(MESSAGE_COUNT_ENDPOINT)

    async def async_get_inverter_counts(self) -> dict[str, Any]:
        return await self._authenticated_get(INVERTER_COUNT_ENDPOINT)

    async def async_get_generation_use(self) -> dict[str, Any]:
        path = GEN_USE_ENDPOINT.format(plant_id=self._plant_id)
        return await self._authenticated_get(path)

    async def async_get_inverter_summary(self) -> dict[str, Any]:
        params = {"lan": self._lan, "sn": self._inverter_sn}
        path = INVERTER_SUMMARY_ENDPOINT.format(sn=self._inverter_sn)
        return await self._authenticated_get(path, params=params)

    # -------------------------------------------------------------------------
    # Core HTTP helpers
    # -------------------------------------------------------------------------

    async def _authenticated_get(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        await self._ensure_token()
        headers = {"Authorization": f"Bearer {self._access_token}"}
        return await self._request("GET", path, params=params, headers=headers)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_body: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        require_success: bool = True,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        _LOGGER.debug(
            "Sunsynk API request: %s %s (params=%s)",
            method,
            path,
            params if params else "{}",
        )
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=30,
            ) as response:
                payload = await self._parse_json(response)
        except ClientError as exc:
            _LOGGER.error("HTTP error calling %s %s: %s", method, path, exc)
            raise SunsynkApiError(f"Network error calling {path}") from exc

        if not require_success:
            return payload

        if response.status != 200:
            _LOGGER.error("HTTP %s calling %s: %s", response.status, path, payload)
            raise SunsynkApiError(
                f"HTTP {response.status} calling {path}", status=response.status, payload=payload
            )

        api_code = payload.get("code")
        if api_code != 0:
            api_msg = payload.get("msg", "Unknown Sunsynk error")
            detail_hint: Optional[str] = None
            data_payload = payload.get("data")
            if isinstance(data_payload, dict):
                detail_hint = (
                    data_payload.get("msg")
                    or data_payload.get("reason")
                    or data_payload.get("message")
                )
            context = f"{api_msg} (endpoint={path}, code={api_code})"
            if detail_hint:
                context = f"{context} - {detail_hint}"
            if "permission" in api_msg.lower():
                context = f"Permission failure on {method} {path}: {context}"
            _LOGGER.warning("Sunsynk API error: %s", context)
            raise SunsynkApiError(context, status=response.status, payload=payload)
        return payload.get("data") or {}

    async def _parse_json(self, response) -> dict[str, Any]:
        text = await response.text()
        try:
            return json.loads(text)  # type: ignore[no-any-return]
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise SunsynkApiError("Invalid JSON response") from exc

    async def _ensure_token(self) -> None:
        async with self._token_lock:
            if self._access_token and time.time() < self._token_expires_at - 30:
                return
            await self._authenticate()

    async def _authenticate(self) -> None:
        _LOGGER.info(
            "Authenticating Sunsynk user %s for plant %s",
            _mask_email(self._email),
            self._plant_id,
        )
        public_key = await self._fetch_public_key()
        encrypted_password = self._encrypt_password(public_key)
        # Generate new nonce and sign for the token request
        # Token sign uses first 10 chars of public key as salt (not POWER_VIEW)
        nonce = int(time.time() * 1000)
        sign_str = f"nonce={nonce}&source={self._source}{public_key[:10]}"
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
        payload = {
            "sign": sign,
            "nonce": nonce,
            "username": self._email,
            "password": encrypted_password,
            "grant_type": "password",
            "client_id": "csp-web",
            "source": self._source,
        }
        data = await self._request(
            "POST",
            "/oauth/token/new",
            json_body=payload,
            require_success=True,
        )
        self._access_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        self._token_expires_at = time.time() + int(expires_in)
        if not self._access_token:
            raise SunsynkApiError("Missing access token in response")

    async def _fetch_public_key(self) -> str:
        nonce = str(int(time.time() * 1000))
        query = f"nonce={nonce}&source={self._source}"
        sign = hashlib.md5((query + "POWER_VIEW").encode("utf-8")).hexdigest()
        path = f"/anonymous/publicKey?{query}&sign={sign}"
        payload = await self._request("GET", path, require_success=True)
        public_key = payload if isinstance(payload, str) else payload.get("data")
        if not public_key:
            raise SunsynkApiError("Failed to obtain Sunsynk public key")
        return public_key

    def _encrypt_password(self, base64_key: str) -> str:
        pem = f"-----BEGIN PUBLIC KEY-----\n{base64_key}\n-----END PUBLIC KEY-----"
        rsa_key = RSA.import_key(pem)
        cipher = PKCS1_v1_5.new(rsa_key)
        encrypted = cipher.encrypt(self._password.encode("utf-8"))
        return base64.b64encode(encrypted).decode("ascii")

    def _format_params(
        self, params: Optional[dict[str, str]]
    ) -> Optional[dict[str, str]]:
        if not params:
            return None
        context = {
            "sn": self._inverter_sn,
            "lan": self._lan,
            "plant_id": self._plant_id,
        }
        rendered: dict[str, str] = {}
        for key, value in params.items():
            rendered[key] = value.format(**context)
        return rendered


def _mask_email(email: str) -> str:
    """Return masked email for logging."""
    if "@" not in email:
        return "***"
    name, domain = email.split("@", 1)
    return f"{name[:1]}***@{domain}"
