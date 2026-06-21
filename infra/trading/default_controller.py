import datetime as dt

from core.domain._types import Hotkey
from infra.trading.execution import execute_trade

class DefaultController:
    def execute_trade(self, window_title: str, hotkey: Hotkey) -> dict:
        try:
            execute_trade(window_title, hotkey)
            return {"timestamp": dt.datetime.now().isoformat(), "status": "success"}
        except Exception as e:
            return {"timestamp": dt.datetime.now().isoformat(), "status": "error", "message": str(e)}
