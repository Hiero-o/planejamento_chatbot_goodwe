from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from pathlib import Path
from typing import Any


class UserStore:
    """Autenticacao inicial local; substitua por Firebase antes de producao."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else Path(__file__).with_name("usuarios.json")
        self.users: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    @staticmethod
    def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
        salt = salt or secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return salt.hex(), digest.hex()

    def register(self, user_id: str, password: str) -> None:
        if not user_id or len(password) < 8:
            raise ValueError("Informe um ID e uma senha com no minimo 8 caracteres")
        if user_id in self.users:
            raise ValueError("Usuario ja cadastrado")
        salt, password_hash = self._hash_password(password)
        self.users[user_id] = {"salt": salt, "password_hash": password_hash}
        self.path.write_text(json.dumps(self.users, indent=2), encoding="utf-8")

    def authenticate(self, user_id: str, password: str) -> bool:
        record = self.users.get(user_id)
        if not record:
            return False
        salt, expected = self._hash_password(password, bytes.fromhex(record["salt"]))
        return hmac.compare_digest(expected, record["password_hash"])
