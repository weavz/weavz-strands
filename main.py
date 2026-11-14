from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from fixture.harness import CODE_EXAMPLE, FixtureServer, assert_fixture_result


def names_for(mode: str) -> set[str]:
    return {"demo__lookup_record"} if mode == "tools" else {"weavz_search", "weavz_read_api", "weavz_execute"}


def run_agent(prompt: str, tools: list[object]) -> object:
    model_id = os.environ.get("WEAVZ_MODEL")
    if not model_id:
        raise RuntimeError("Set WEAVZ_MODEL to a Bedrock model id and configure AWS credentials")
    return Agent(model=BedrockModel(model_id=model_id), tools=tools)(prompt)


async def exercise(mode: str, url: str, token: str, *, fixture: bool = False, prompt: str | None = None) -> None:
    with MCPClient(url=url, headers={"Authorization": f"Bearer {token}"}) as client:
        tools = client.list_tools_sync()
        names = {getattr(tool, "name", None) or tool.tool_spec["name"] for tool in tools}
        if fixture and not names_for(mode).issubset(names):
            raise RuntimeError(f"Expected fixture tools {sorted(names_for(mode))}; got {sorted(names)}")
        if not fixture and prompt is None:
            print(json.dumps({"proof": "live Weavz MCP tool discovery", "mode": mode, "tools": sorted(names)}))
            return
        if prompt:
            print(run_agent(prompt, tools))
            return
        if mode == "tools":
            result = client.call_tool_sync("fixture-check", "demo__lookup_record", {"recordId": "record-1"})
            assert_fixture_result(mode, result)
            results = {"lookup": str(result)}
        else:
            search = client.call_tool_sync("fixture-search", "weavz_search", {"query": "fixture"})
            read_api = client.call_tool_sync("fixture-read-api", "weavz_read_api", {"alias": "demo", "action": "lookup_record"})
            result = client.call_tool_sync("fixture-execute", "weavz_execute", {"code": CODE_EXAMPLE})
            assert_fixture_result(mode, search)
            assert_fixture_result(mode, result)
            results = {"search": str(search), "read_api": str(read_api), "execute": str(result)}
        print(json.dumps({"proof": "local fixture adapter calls", "mode": mode, "tools": sorted(names), "results": results}))


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--mode", choices=("tools", "code"), default=os.getenv("WEAVZ_MCP_MODE", "tools"))
    parser.add_argument("--prompt")
    args = parser.parse_args()
    if args.fixture:
        if args.prompt:
            raise SystemExit("--prompt uses a model provider; run without --fixture for a live model run")
        with FixtureServer(args.mode) as fixture:
            fixture.reject_bad_token()
            await exercise(args.mode, fixture.url, "local-fixture-token", fixture=True)
    else:
        url, token = os.getenv("WEAVZ_MCP_URL"), os.getenv("WEAVZ_MCP_TOKEN")
        if not url or not token:
            raise SystemExit("Set WEAVZ_MCP_URL and WEAVZ_MCP_TOKEN from your custom Weavz setup")
        if token.startswith("wvz_"):
            raise SystemExit("WEAVZ_MCP_TOKEN must be an MCP access token, not a Weavz REST API key")
        if urlparse(url).scheme != "https" and urlparse(url).hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise SystemExit("Use an HTTPS MCP URL except for loopback development")
        await exercise(args.mode, url, token, prompt=args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
