from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from external.ngrok.env_loader import load_env_file


@dataclass(frozen=True)
class NgrokSettings:
    ngrok_authtoken: str
    ngrok_domain: str
    proxy_host: str = "127.0.0.1"
    proxy_port: int = 8080
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    allowed_prefix: str = "/api/v1"

    @property
    def proxy_url(self) -> str:
        return f"http://{self.proxy_host}:{self.proxy_port}"

    @property
    def api_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}"

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "NgrokSettings":
        root = Path.cwd()
        env = load_env_file(root / env_file)

        def get(key: str, default: str | None = None) -> str | None:
            if key in os.environ:
                return os.environ[key]
            return env.get(key, default)

        token = get("NGROK_AUTHTOKEN")
        domain = get("NGROK_DOMAIN")
        if not token:
            raise ValueError("Missing NGROK_AUTHTOKEN in environment or .env")
        if not domain:
            raise ValueError("Missing NGROK_DOMAIN in environment or .env")

        proxy_host = get("NGROK_PROXY_HOST", "127.0.0.1") or "127.0.0.1"
        proxy_port = int(get("NGROK_PROXY_PORT", "8080") or "8080")
        api_host = get("API_HOST", "127.0.0.1") or "127.0.0.1"
        api_port = int(get("API_PORT", "8000") or "8000")
        allowed_prefix = get("NGROK_ALLOWED_PREFIX", "/api/v1") or "/api/v1"

        return cls(
            ngrok_authtoken=token,
            ngrok_domain=domain,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            api_host=api_host,
            api_port=api_port,
            allowed_prefix=allowed_prefix,
        )
