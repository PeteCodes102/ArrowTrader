from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI

from core.services.trader import Trader

from api.v1.router import router as v1_router

@dataclass(frozen=True)
class ApiSettings:
    title: str = "Arrow Trader API"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

def register_routers(app: FastAPI) -> None:
    app.include_router(v1_router, prefix="/api/v1")


def create_app(settings: ApiSettings | None = None, trader: Trader | None = None) -> FastAPI:
    cfg = settings or ApiSettings()
    app = FastAPI(
        title=cfg.title,
        version=cfg.version,
        docs_url=cfg.docs_url,
        redoc_url=cfg.redoc_url,
        openapi_url=cfg.openapi_url,
    )

    register_routers(app)
    if trader is not None:
        app.state.trader = trader
    return app
