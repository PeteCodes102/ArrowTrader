from __future__ import annotations

from dataclasses import dataclass

from external.ngrok.config import NgrokSettings
from external.ngrok.proxy_server import ProxyServer
from external.ngrok.tunnel import NgrokTunnel


@dataclass
class NgrokRuntimeState:
    proxy_url: str
    public_url: str
    domain: str


class NgrokOrchestrator:
    def __init__(self, settings: NgrokSettings | None = None) -> None:
        self._settings = settings or NgrokSettings.from_env()
        self._proxy = ProxyServer(self._settings)
        self._tunnel = NgrokTunnel(self._settings)
        self._state: NgrokRuntimeState | None = None

    @property
    def state(self) -> NgrokRuntimeState | None:
        return self._state

    def start(self) -> NgrokRuntimeState:
        self._proxy.start()
        public_url = self._tunnel.start()
        self._state = NgrokRuntimeState(
            proxy_url=self._settings.proxy_url,
            public_url=public_url,
            domain=self._settings.ngrok_domain,
        )
        return self._state

    def stop(self) -> None:
        self._tunnel.stop()
        self._proxy.stop()
