from __future__ import annotations

from pyngrok import ngrok

from external.ngrok.config import NgrokSettings


class NgrokTunnel:
    def __init__(self, settings: NgrokSettings) -> None:
        self._settings = settings
        self.public_url: str | None = None

    def start(self) -> str:
        ngrok.set_auth_token(self._settings.ngrok_authtoken)
        tunnel = ngrok.connect(
            addr=self._settings.proxy_url,
            bind_tls=True,
            domain=self._settings.ngrok_domain,
        )
        self.public_url = tunnel.public_url
        return self.public_url

    def stop(self) -> None:
        if self.public_url:
            ngrok.disconnect(self.public_url)
            self.public_url = None
