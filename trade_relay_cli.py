from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import datetime, timezone
from typing import Any
from urllib import error, request

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


COMMAND_MAP = {
    "b": "buy",
    "s": "sell",
    "e": "exit",
    "r": "reverse",
}


class RelayInput(BaseModel):
    command: str


class RelayClient:
    def __init__(
        self,
        target_url: str,
        secret: str | None = None,
        contract: str | None = None,
        quantity: int = 1,
        price: float = 30000,
    ) -> None:
        self.target_url = target_url.rstrip("/")
        self.secret = (secret or "").strip() or None
        self.contract = (contract or "NQ1").strip() or "NQ1"
        self.quantity = int(quantity)
        self.price = float(price)

    def send_action(self, action: str) -> tuple[int, str]:
        payload: dict[str, Any] = {
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quantity": self.quantity,
            "price": self.price,
        }
        if self.secret:
            payload["secret"] = self.secret
        if self.contract:
            payload["contract"] = self.contract

        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.target_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=10) as resp:
                status = getattr(resp, "status", 200)
                raw = resp.read().decode("utf-8", errors="replace")
                return status, raw
        except error.HTTPError as http_exc:
            raw = http_exc.read().decode("utf-8", errors="replace")
            return http_exc.code, raw
        except Exception as exc:
            return 0, f"Request failed: {exc}"


class RelayServer:
    def __init__(self, client: RelayClient, host: str, port: int) -> None:
        self.client = client
        self.host = host
        self.port = port
        self.app = self._build_app()
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None

    def _build_app(self) -> FastAPI:
        app = FastAPI(title="Trade Relay CLI", version="1.0.0")

        @app.get("/health")
        def health() -> dict[str, str]:
            return {
                "status": "ok",
                "target_url": self.client.target_url,
            }

        @app.post("/send/{command}")
        def send_by_path(command: str) -> dict[str, Any]:
            normalized = command.strip().lower()
            action = COMMAND_MAP.get(normalized)
            if action is None:
                raise HTTPException(status_code=400, detail="Command must be one of: b, s, e, r")
            status, body = self.client.send_action(action)
            return {
                "command": normalized,
                "action": action,
                "upstream_status": status,
                "upstream_response": body,
            }

        @app.post("/send")
        def send_by_body(data: RelayInput) -> dict[str, Any]:
            normalized = data.command.strip().lower()
            action = COMMAND_MAP.get(normalized)
            if action is None:
                raise HTTPException(status_code=400, detail="Command must be one of: b, s, e, r")
            status, body = self.client.send_action(action)
            return {
                "command": normalized,
                "action": action,
                "upstream_status": status,
                "upstream_response": body,
            }

        return app

    def start(self) -> None:
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        time.sleep(0.2)

    def stop(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)


def print_instructions(target_url: str, host: str, port: int) -> None:
    print("\nTrade Relay CLI")
    print("=" * 60)
    print(f"Target URL: {target_url}")
    print(f"Relay API:   http://{host}:{port}")
    print("Payload defaults: quantity=1, price=30000, contract=NQ1")
    print("\nCommands:")
    print("  b  -> send BUY")
    print("  s  -> send SELL")
    print("  e  -> send EXIT")
    print("  r  -> send REVERSE")
    print("  h  -> show this help")
    print("  q  -> quit")
    print("\nRelay endpoints:")
    print("  GET  /health")
    print("  POST /send/{b|s|e|r}")
    print("  POST /send   with JSON: {\"command\": \"b\"}")
    print("=" * 60)


def handle_cli_input(client: RelayClient) -> None:
    while True:
        cmd = input("\nEnter command [b/s/e/r/h/q]: ").strip().lower()
        if cmd in {"q", "quit", "exit"}:
            print("Exiting relay CLI.")
            return
        if cmd in {"h", "help", "?"}:
            print("b=buy, s=sell, e=exit, r=reverse, q=quit")
            continue

        action = COMMAND_MAP.get(cmd)
        if action is None:
            print("Invalid command. Use b, s, e, r, h, or q.")
            continue

        print(f"Sending {action.upper()} to target...")
        status, response = client.send_action(action)
        print(f"Response status: {status}")
        print(f"Response body:   {response}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start a local FastAPI relay and interactive command terminal for trade actions.",
    )
    parser.add_argument("url", nargs="?", help="Target webhook URL to receive trade requests.")
    parser.add_argument("--url", "-url", dest="url_flag", default="", help="Target webhook URL.")
    parser.add_argument("--secret", default="", help="Optional secret to include in each payload.")
    parser.add_argument("--contract", default="NQ1", help="Contract to include in each payload (default: NQ1).")
    parser.add_argument("--quantity", type=int, default=1, help="Order quantity (default: 1).")
    parser.add_argument("--price", type=float, default=30000, help="Order price (default: 30000).")
    parser.add_argument("--host", default="127.0.0.1", help="Relay server host.")
    parser.add_argument("--port", type=int, default=8765, help="Relay server port.")
    args = parser.parse_args()
    target_url = (args.url_flag or args.url or "").strip()
    if not target_url:
        parser.error("A target URL is required. Provide positional url or --url.")
    args.url = target_url
    return args


def main() -> None:
    args = parse_args()
    client = RelayClient(
        args.url,
        secret=args.secret,
        contract=args.contract,
        quantity=args.quantity,
        price=args.price,
    )
    relay = RelayServer(client, host=args.host, port=args.port)

    relay.start()
    print_instructions(client.target_url, args.host, args.port)

    try:
        handle_cli_input(client)
    except KeyboardInterrupt:
        print("\nInterrupted. Shutting down.")
    finally:
        relay.stop()


if __name__ == "__main__":
    main()
