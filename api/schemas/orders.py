from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    contract: str | None = Field(None, description="Contract/symbol identifier.")
    quantity: int = Field(..., ge=1, description="Number of units/contracts.")
    price: float = Field(..., gt=0, description="Requested/last price.")
    secret: str = Field(
        ...,
        validation_alias=AliasChoices("secret", "spam-key", "alert_id"),
        description="Auth secret. Accepts 'secret', 'spam-key', or 'alert_id'.",
    )
    trade_type: Literal["buy", "sell", "exit", "reverse"] = Field(
        ...,
        validation_alias=AliasChoices("trade_type", "action"),
        description="Trading action. Accepts 'trade_type' or 'action'. 'flatten' normalises to 'exit'.",
    )

    @field_validator("trade_type", mode="before")
    @classmethod
    def _normalise_trade_type(cls, v: object) -> object:
        if v == "flatten":
            return "exit"
        return v


class OrderResponse(BaseModel):
    status: str
    trade_type: str
    timestamp: str | None = None
    detail: str | None = None
    window_name: str | None = None
    controller_status: str | None = None
    latency_ms: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
