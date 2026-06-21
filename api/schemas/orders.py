from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field
from pydantic.config import ConfigDict


class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    contract: str = Field(..., description="Contract/symbol identifier.")
    quantity: int = Field(..., ge=1, description="Number of units/contracts.")
    price: float = Field(..., gt=0, description="Requested/last price.")
    secret: str = Field(
        ...,
        validation_alias=AliasChoices("secret", "spam-key"),
        description="Authentication secret from the GUI Secret field. Accepts either 'secret' or 'spam-key'.",
    )
    trade_type: Literal["buy", "sell", "exit", "reverse"] = Field(
        ...,
        description="Trading action to execute.",
    )


class OrderResponse(BaseModel):
    status: str
    trade_type: str
    timestamp: str | None = None
    detail: str | None = None
    window_name: str | None = None
    controller_status: str | None = None
    latency_ms: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
