from __future__ import annotations

from fastapi import APIRouter

from api.v1.endpoints.health import router as health_router
from api.v1.endpoints.orders import router as orders_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(orders_router, tags=["orders"])
