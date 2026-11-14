from __future__ import annotations

import argparse
import json
import os
from typing import Any

import uvicorn
from mcp.server import MCPServer
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

RECORD = {"recordId": "record-1", "title": "Synthetic fixture record", "status": "open"}
CODE_EXAMPLE = 'return await weavz.demo.lookup_record({recordId: "record-1"});'


class BearerOnly:
    """Small raw ASGI gate; no HTTP middleware that wraps streaming receive/send."""

    def __init__(self, app: ASGIApp, token: str):
        self.app = app
        self.token = token.encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path") == "/mcp":
            headers = dict(scope.get("headers", []))
            if headers.get(b"authorization") != b"Bearer " + self.token:
                body = json.dumps({"error": "unauthorized"}).encode()
                response = JSONResponse({"error": "unauthorized"}, status_code=401)
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


def build_app(mode: str, token: str) -> ASGIApp:
    server = MCPServer("Weavz Python Example Fixture", version="0.1.0")

    if mode == "tools":
        @server.tool(name="demo__lookup_record")
        def lookup_record(recordId: str) -> dict[str, str]:
            """Look up the single synthetic fixture record by its ID."""
            if recordId != RECORD["recordId"]:
                raise ValueError("Only record-1 exists in this local fixture")
            return dict(RECORD)
    else:
        @server.tool()
        def weavz_search(query: str) -> list[dict[str, str]]:
            """Search the synthetic local fixture records."""
            if query.casefold() not in {"fixture", "record-1", "synthetic"}:
                return []
            return [dict(RECORD)]

        @server.tool()
        def weavz_read_api(alias: str | None = None, aliases: list[str] | None = None,
                           action: str | None = None) -> dict[str, Any]:
            """Inspect the one read-only demo API alias and its action."""
            selected = aliases or ([alias] if alias else [])
            if selected and any(item != "demo" for item in selected):
                raise ValueError("The fixture only advertises alias demo")
            return {"aliases": ["demo"], "action": action or "lookup_record"}

        @server.tool()
        def weavz_execute(code: str) -> list[dict[str, str]]:
            """Run only the documented, fixed lookup snippet; arbitrary code is rejected."""
            if code.strip() != CODE_EXAMPLE:
                raise ValueError("Fixture accepts only the documented demo lookup snippet")
            return [dict(RECORD)]

    app = server.streamable_http_app()

    # Add a health route and wrap the MCP ASGI app directly to preserve the SDK's
    # streaming channel semantics and lifespan.
    async def app_with_health(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path") == "/health":
            response = JSONResponse({"status": "ok", "mode": mode})
            await response(scope, receive, send)
            return
        await app(scope, receive, send)

    return BearerOnly(app_with_health, token)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("tools", "code"), required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    token = os.environ.get("MCP_TOKEN", "")
    if not token:
        raise SystemExit("MCP_TOKEN is required for the local fixture")
    uvicorn.run(build_app(args.mode, token), host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
