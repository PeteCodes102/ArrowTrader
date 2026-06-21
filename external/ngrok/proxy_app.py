from __future__ import annotations

import httpx

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from external.ngrok.config import NgrokSettings

_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _build_target_url(settings: NgrokSettings, path: str, query: str) -> str:
    suffix = f"/{path}" if path else ""
    base = f"{settings.api_url}{settings.allowed_prefix}{suffix}"
    if query:
        return f"{base}?{query}"
    return base


def _filter_response_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in _HOP_BY_HOP_HEADERS and k.lower() != "content-length"
    }


def _build_upstream_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in {"host", "content-length"} and k.lower() not in _HOP_BY_HOP_HEADERS
    }


def create_proxy_app(settings: NgrokSettings) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.on_event("startup")
    async def _startup() -> None:
        app.state.http_client = httpx.AsyncClient(timeout=6.0)

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        client: httpx.AsyncClient | None = getattr(app.state, "http_client", None)
        if client is not None:
            await client.aclose()

    @app.api_route(f"{settings.allowed_prefix}", methods=_METHODS)
    async def proxy_root(request: Request) -> Response:
        return await _forward(request, settings, "")

    @app.api_route(f"{settings.allowed_prefix}/{{path:path}}", methods=_METHODS)
    async def proxy_path(path: str, request: Request) -> Response:
        return await _forward(request, settings, path)

    @app.api_route("/{path:path}", methods=_METHODS)
    async def block_other_paths(path: str) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    return app


async def _forward(request: Request, settings: NgrokSettings, path: str) -> Response:
    body = await request.body()
    url = _build_target_url(settings, path, request.url.query)
    client: httpx.AsyncClient = request.app.state.http_client

    try:
        upstream = await client.request(
            method=request.method,
            url=url,
            content=body,
            headers=_build_upstream_headers(dict(request.headers)),
        )
    except httpx.HTTPError as exc:
        return JSONResponse(status_code=502, content={"detail": f"Proxy forward failed: {exc}"})

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=_filter_response_headers(dict(upstream.headers.items())),
    )
