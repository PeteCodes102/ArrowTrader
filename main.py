from core.services.trader import Trader
from api.app import create_app
from external.ngrok import NgrokOrchestrator
from infra.gui import ArrowTraderApp
from infra.trading.default_controller import DefaultController

import asyncio
import threading
import uvicorn


def _start_api_server(trader: Trader) -> None:
    api_app = create_app(trader=trader)
    config = uvicorn.Config(
        app=api_app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()

if __name__ == "__main__":
    app = ArrowTraderApp()
    controller = DefaultController()
    trader = Trader(controller=controller, app=app)
    _start_api_server(trader)
    app.log("API listening on http://127.0.0.1:8000/api/v1")

    ngrok_orchestrator: NgrokOrchestrator | None = None
    try:
        ngrok_orchestrator = NgrokOrchestrator()
        ngrok_state = ngrok_orchestrator.start()
        app.log(f"Public API proxy: {ngrok_state.proxy_url}{'/api/v1'}")
        app.log(f"Ngrok public endpoint: {ngrok_state.public_url}/api/v1")
    except Exception as exc:
        app.log(f"Ngrok startup skipped: {exc}")

    for action in ("buy", "sell", "exit", "reverse"):
        def _launch_action(selected_action: str = action) -> None:
            def _worker() -> None:
                try:
                    asyncio.run(trader.execute(selected_action))
                except Exception as exc:
                    app.log(f"Action failed for {selected_action}: {exc}")

            threading.Thread(target=_worker, daemon=True).start()

        app.action_buttons.set_command(action, _launch_action)

    def _on_close() -> None:
        if ngrok_orchestrator is not None:
            try:
                ngrok_orchestrator.stop()
            except Exception as exc:
                app.log(f"Ngrok shutdown warning: {exc}")
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", _on_close)
    app.run()