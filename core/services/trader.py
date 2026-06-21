from __future__ import annotations

import asyncio
import datetime as dt
import hmac
import time
from typing import Any

from core.domain._types import Hotkey
from core.domain.hotkey import parse_hotkey
from core.ports.controller import Controller
from core.ports.main_app import MainApp


class Trader:
    def __init__(self, controller: Controller, app: MainApp) -> None:
        self._controller = controller
        self._app = app
        self._hotkey_cache: dict[str, tuple[str, Hotkey]] = {}

    async def execute(self, action: str, order_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        trader_start_ns = time.perf_counter_ns()
        raw = self._app.hotkeys.get(action)
        if not raw:
            raise ValueError(f"No hotkey configured for action: {action!r}")

        window_name = self._app.window_name
        hotkey = self._resolve_hotkey(action, raw)

        loop = asyncio.get_running_loop()
        controller_start_ns = time.perf_counter_ns()
        controller_result = await loop.run_in_executor(
            None,
            self._controller.execute_trade,
            window_name,
            hotkey,
        )
        controller_end_ns = time.perf_counter_ns()

        if isinstance(controller_result, dict) and controller_result.get("status") == "error":
            message = controller_result.get("message", "Controller execution failed.")
            self._app.log(f"Execution failed: {message}", action=action)
            raise RuntimeError(str(message))

        success_msg = {
            "status": "success",
            "trade_type": action,
            "timestamp": dt.datetime.now().isoformat(),
            "window_name": window_name,
            "controller_status": "success",
        }

        if isinstance(controller_result, dict):
            success_msg["controller_status"] = controller_result.get("status", "success")

        success_msg["latency_ms"] = {
            "controller_exec_ms": round((controller_end_ns - controller_start_ns) / 1_000_000, 3),
            "trader_total_ms": round((time.perf_counter_ns() - trader_start_ns) / 1_000_000, 3),
        }

        log_line = self._build_log_line(
            action,
            order_payload,
            window_name,
            success_msg["timestamp"],
            success_msg["latency_ms"],
        )
        self._app.log(log_line, action=action)

        if order_payload:
            success_msg["metadata"] = {
                "contract": order_payload.get("contract"),
                "quantity": order_payload.get("quantity"),
                "price": order_payload.get("price"),
            }

        return success_msg

    def _resolve_hotkey(self, action: str, raw: str) -> Hotkey:
        cached = self._hotkey_cache.get(action)
        if cached and cached[0] == raw:
            return cached[1]

        parsed = parse_hotkey(raw)
        self._hotkey_cache[action] = (raw, parsed)
        return parsed

    @property
    def secret_is_configured(self) -> bool:
        return bool(self._app.secret.strip())

    def validate_secret(self, presented_secret: str | None) -> bool:
        if presented_secret is None:
            return False
        expected = self._app.secret
        if not expected:
            return False
        return hmac.compare_digest(presented_secret.strip(), expected.strip())

    @property
    def trader_enabled(self) -> bool:
        return self._app.trader_enabled

    def _build_log_line(
        self,
        action: str,
        order_payload: dict[str, Any] | None,
        window_name: str,
        timestamp: str,
        latency_ms: dict[str, float] | None = None,
    ) -> str:
        suffix = ""
        if latency_ms:
            suffix = (
                f" | t_ctrl={latency_ms.get('controller_exec_ms', 0):.3f}ms"
                f" t_trader={latency_ms.get('trader_total_ms', 0):.3f}ms"
            )

        if not order_payload:
            return f"Executed {action} on '{window_name}' at {timestamp}{suffix}"

        contract = order_payload.get("contract")
        quantity = order_payload.get("quantity")
        price = order_payload.get("price")
        return (
            f"Executed {action} | contract={contract} qty={quantity} "
            f"price={price} | window='{window_name}' | {timestamp}{suffix}"
        )
