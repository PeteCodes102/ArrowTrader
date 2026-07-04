import asyncio
from dataclasses import dataclass
import os
from pathlib import Path
import socket
import threading
from urllib.parse import SplitResult, urlsplit, urlunsplit
import uvicorn

from api.app import create_app
from core.services.trader import Trader
from infra.gui import ArrowTraderApp
from infra.trading.default_controller import DefaultController


@dataclass(frozen=True)
class RuntimeSettings:
    api_host: str
    api_port: int
    api_public_url: str
    requested_api_port: int
    port_auto_adjusted: bool


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    loaded: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            loaded[key] = value
    return loaded


def _load_runtime_settings(env_file: str = ".env") -> RuntimeSettings:
    env_from_file = _load_env_file(Path(env_file))

    def get(name: str, default: str) -> str:
        return os.environ.get(name, env_from_file.get(name, default))

    api_host = get("API_HOST", "0.0.0.0") or "0.0.0.0"
    requested_port = int(get("API_PORT", "8000") or "8000")

    api_port = requested_port
    port_auto_adjusted = False
    if not _is_bind_available(api_host, requested_port):
        fallback_port = _find_open_port(api_host, requested_port + 1, requested_port + 20)
        if fallback_port is None:
            raise RuntimeError(
                "No available API port found. Free API_PORT or set a different one in .env."
            )
        api_port = fallback_port
        port_auto_adjusted = True

    tailscale_url = (get("TAILSCALE_API_URL", "") or "").strip().rstrip("/")
    public_host = "127.0.0.1" if api_host in {"0.0.0.0", "::"} else api_host
    local_url = f"http://{public_host}:{api_port}/api/v1"
    if tailscale_url:
        api_public_url = _rewrite_url_port(tailscale_url, api_port)
    else:
        api_public_url = local_url

    return RuntimeSettings(
        api_host=api_host,
        api_port=api_port,
        api_public_url=api_public_url,
        requested_api_port=requested_port,
        port_auto_adjusted=port_auto_adjusted,
    )


def _is_bind_available(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
        return True
    except OSError:
        return False


def _find_open_port(host: str, start_port: int, end_port: int) -> int | None:
    for candidate in range(start_port, end_port + 1):
        if _is_bind_available(host, candidate):
            return candidate
    return None


def _rewrite_url_port(url: str, port: int) -> str:
    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.hostname:
        return url

    # Keep public Funnel-style URLs untouched when no explicit port was set.
    if parsed.port is None:
        return url.rstrip("/")

    auth_prefix = ""
    if parsed.username:
        auth_prefix = parsed.username
        if parsed.password:
            auth_prefix += f":{parsed.password}"
        auth_prefix += "@"

    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    new_netloc = f"{auth_prefix}{host}:{port}"
    rewritten = SplitResult(
        scheme=parsed.scheme,
        netloc=new_netloc,
        path=parsed.path,
        query=parsed.query,
        fragment=parsed.fragment,
    )
    return urlunsplit(rewritten).rstrip("/")


def _start_api_server(trader: Trader, settings: RuntimeSettings) -> None:
    api_app = create_app(trader=trader)
    config = uvicorn.Config(
        app=api_app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()


if __name__ == "__main__":
    settings = _load_runtime_settings()
    app = ArrowTraderApp(default_api_url=settings.api_public_url)
    app.window_input.set_api_url(settings.api_public_url)
    controller = DefaultController()
    trader = Trader(controller=controller, app=app)
    _start_api_server(trader, settings)
    if settings.port_auto_adjusted:
        app.log(
            "Configured API_PORT was in use; auto-selected "
            f"{settings.api_port} instead of {settings.requested_api_port}."
        )
    app.log(f"API listener: http://{settings.api_host}:{settings.api_port}/api/v1")
    app.log(f"Configured API URL: {settings.api_public_url}")

    for action in ("buy", "sell", "exit", "reverse"):
        def _launch_action(selected_action: str = action) -> None:
            def _worker() -> None:
                try:
                    asyncio.run(trader.execute(selected_action))
                except Exception as exc:
                    app.log(f"Action failed for {selected_action}: {exc}")

            threading.Thread(target=_worker, daemon=True).start()

        app.action_buttons.set_command(action, _launch_action)

    def _on_close() -> None:
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", _on_close)
    app.run()