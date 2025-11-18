import asyncio
import base64
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import urlsplit

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from custom_components.sunsynk_sync.api_client import SunsynkApiClient  # noqa: E402


class FakeResponse:
    def __init__(self, status: int, payload: Dict[str, Any]) -> None:
        self.status = status
        self._payload = payload

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def text(self) -> str:
        return json_dumps(self._payload)


def json_dumps(payload: Dict[str, Any]) -> str:
    import json

    return json.dumps(payload)


@dataclass
class ResponsePayload:
    status: int
    body: Dict[str, Any]


class FakeSession:
    def __init__(self, responses: Dict[Tuple[str, str], ResponsePayload]) -> None:
        self._responses = responses
        self.calls: list[Tuple[str, str]] = []

    def request(self, method: str, url: str, **_: Any) -> FakeResponse:
        parsed = urlsplit(url)
        path = parsed.path
        key = (method.upper(), path)
        # `/anonymous/publicKey` includes query string, normalize to base path
        if path == "/anonymous/publicKey":
            key = (method.upper(), "/anonymous/publicKey")

        payload = self._responses.get(key)
        if not payload:
            raise AssertionError(f"Unexpected request: {method} {path}")
        self.calls.append((method.upper(), path))
        return FakeResponse(payload.status, payload.body)


def _build_public_key() -> Tuple[str, RSA.RsaKey]:
    key = RSA.generate(1024)
    der = key.publickey().export_key(format="DER")
    return base64.b64encode(der).decode("ascii"), key


def test_encrypt_password_roundtrip() -> None:
    public_b64, rsa_key = _build_public_key()
    session = FakeSession({})
    client = SunsynkApiClient(
        session,
        email="user@example.com",
        password="supersecret",
        plant_id="221135",
        inverter_sn="2302100572",
    )

    encrypted = client._encrypt_password(public_b64)
    cipher = PKCS1_v1_5.new(rsa_key)
    decoded = cipher.decrypt(base64.b64decode(encrypted), b"").decode("utf-8")
    assert decoded == "supersecret"


def test_flow_request_performs_authentication(monkeypatch) -> None:
    public_b64, _ = _build_public_key()
    responses = {
        ("GET", "/anonymous/publicKey"): ResponsePayload(
            200,
            {"code": 0, "msg": "Success", "data": public_b64},
        ),
        ("POST", "/oauth/token/new"): ResponsePayload(
            200,
            {
                "code": 0,
                "msg": "Success",
                "data": {"access_token": "token-value", "expires_in": 60},
            },
        ),
        ("GET", "/api/v1/inverter/SN123/flow"): ResponsePayload(
            200,
            {
                "code": 0,
                "msg": "Success",
                "data": {"pvPower": 1234, "soc": 55.0},
            },
        ),
    }
    session = FakeSession(responses)
    client = SunsynkApiClient(
        session,
        email="user@example.com",
        password="secret",
        plant_id="PID",
        inverter_sn="SN123",
    )

    async def run() -> Dict[str, Any]:
        monkeypatch.setattr(client, "_encrypt_password", lambda _: "encrypted")
        return await client.async_get_flow()

    data = asyncio.run(run())
    assert data["pvPower"] == 1234
    assert ("GET", "/api/v1/inverter/SN123/flow") in session.calls
