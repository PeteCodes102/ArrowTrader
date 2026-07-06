from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_trader
from api.schemas.orders import OrderRequest, OrderResponse
from core.services.trader import Trader

router = APIRouter()


def _reject_when_trader_is_off(trader: Trader) -> None:
    if trader.trader_enabled:
        return

    trader._app.log("Rejected API order because trader power is OFF.")
    raise HTTPException(
        status_code=503,
        detail="Trader is OFF. API order intake is disabled until trader power is turned back on.",
    )


def _reject_when_outside_session(trader: Trader) -> None:
    allowed, reason = trader.is_within_allowed_session()
    if allowed:
        return

    detail = reason or "Trade rejected by session filter settings."
    trader._app.log(detail)
    raise HTTPException(status_code=503, detail=detail)


def _authorize_or_raise(trader: Trader, presented_secret: str | None) -> None:
    if not trader.secret_is_configured:
        raise HTTPException(
            status_code=503,
            detail="Secret is not configured in the GUI.",
        )

    if not presented_secret:
        raise HTTPException(
            status_code=401,
            detail="Missing secret. Provide it in the request body field 'secret' or 'spam-key'.",
        )

    if not trader.validate_secret(presented_secret):
        raise HTTPException(status_code=401, detail="Invalid secret.")


@router.post("/orders", response_model=OrderResponse)
async def place_order(
    payload: OrderRequest,
    trader: Trader = Depends(get_trader),
) -> OrderResponse:
    request_start_ns = time.perf_counter_ns()
    _reject_when_trader_is_off(trader)
    _reject_when_outside_session(trader)

    auth_start_ns = time.perf_counter_ns()
    _authorize_or_raise(trader, payload.secret)
    auth_end_ns = time.perf_counter_ns()

    execute_start_ns = time.perf_counter_ns()
    try:
        result = await trader.execute(payload.trade_type, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to execute order: {exc}")
    execute_end_ns = time.perf_counter_ns()

    latency_ms = {
        "api_auth_ms": round((auth_end_ns - auth_start_ns) / 1_000_000, 3),
        "api_execute_await_ms": round((execute_end_ns - execute_start_ns) / 1_000_000, 3),
        "api_total_ms": round((execute_end_ns - request_start_ns) / 1_000_000, 3),
    }

    trader_latency = result.get("latency_ms")
    if isinstance(trader_latency, dict):
        for key, value in trader_latency.items():
            if isinstance(value, (int, float)):
                latency_ms[key] = float(value)

    return OrderResponse(
        status=result.get("status", "unknown"),
        trade_type=result.get("trade_type", payload.trade_type),
        timestamp=result.get("timestamp"),
        detail=result.get("detail"),
        window_name=result.get("window_name"),
        controller_status=result.get("controller_status"),
        latency_ms=latency_ms,
        metadata=result.get("metadata"),
    )
