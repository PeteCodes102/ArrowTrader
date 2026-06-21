from __future__ import annotations

from fastapi import HTTPException, Request, status

from core.services.trader import Trader


def get_trader(request: Request) -> Trader:
    trader = getattr(request.app.state, "trader", None)
    if trader is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Trader service is not attached to API app state.",
        )
    return trader
