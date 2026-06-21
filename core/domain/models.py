from pydantic import BaseModel, ConfigDict

from core.domain._types import WindowName, Hotkey, Timestamp

import datetime as dt

class Order(BaseModel):
    window_title: WindowName
    hotkey: Hotkey

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

class Trade(BaseModel):
    contract: str
    trade_type: str
    quantity: int
    price: float
    timestamp: Timestamp

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

