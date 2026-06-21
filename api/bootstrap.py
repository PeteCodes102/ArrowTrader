from __future__ import annotations

from fastapi import FastAPI

from api.app import create_app
from core.services.trader import Trader

def create_configured_app(trader: Trader) -> FastAPI:
    app = create_app()
    app.state.trader = trader
    return app
