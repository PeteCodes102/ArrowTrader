from __future__ import annotations

import socket
import threading
import time

import uvicorn

from external.ngrok.config import NgrokSettings
from external.ngrok.proxy_app import create_proxy_app


class ProxyServer:
    def __init__(self, settings: NgrokSettings) -> None:
        self._settings = settings
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        app = create_proxy_app(self._settings)
        config = uvicorn.Config(
            app=app,
            host=self._settings.proxy_host,
            port=self._settings.proxy_port,
            log_level="warning",
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        self._wait_until_ready(timeout=5.0)

    def stop(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def _wait_until_ready(self, timeout: float) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.25)
                if sock.connect_ex((self._settings.proxy_host, self._settings.proxy_port)) == 0:
                    return
            time.sleep(0.1)
        raise RuntimeError(
            f"Proxy server did not start on {self._settings.proxy_host}:{self._settings.proxy_port}"
        )
