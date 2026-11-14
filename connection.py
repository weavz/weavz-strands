from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit


def validate_live_connection(url: str | None, token: str | None) -> tuple[str, str]:
    if not url:
        raise ValueError("Set WEAVZ_MCP_URL to your custom Weavz MCP endpoint")
    if not token:
        raise ValueError("Set WEAVZ_MCP_TOKEN to the MCP access token for that endpoint")
    if token.startswith("wvz_"):
        raise ValueError("WEAVZ_MCP_TOKEN must be an MCP access token, not a Weavz REST API key")
    if any(character.isspace() for character in token):
        raise ValueError("WEAVZ_MCP_TOKEN must be non-empty and contain no whitespace")

    try:
        endpoint = urlsplit(url)
        hostname = endpoint.hostname
        endpoint.port  # Validate port syntax and range.
    except ValueError as error:
        raise ValueError("WEAVZ_MCP_URL must be a valid absolute HTTP(S) URL") from error

    if endpoint.username is not None or endpoint.password is not None:
        raise ValueError("WEAVZ_MCP_URL must not contain embedded credentials")
    if "?" in url or "#" in url:
        raise ValueError("WEAVZ_MCP_URL must not contain a query string or fragment")
    if endpoint.scheme not in {"https", "http"} or not hostname or not endpoint.netloc:
        raise ValueError("WEAVZ_MCP_URL must be a valid absolute HTTP(S) URL")
    if endpoint.path.rstrip("/") == "/mcp/weavz":
        raise ValueError("The hosted /mcp/weavz resource uses OAuth; use a custom MCP endpoint")

    loopback = hostname == "localhost"
    if not loopback:
        try:
            loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            loopback = False
    if endpoint.scheme != "https" and not (endpoint.scheme == "http" and loopback):
        raise ValueError("Use an HTTPS MCP URL except for HTTP loopback development")
    return url, token


def validate_catalog(mode: str, names: set[str]) -> None:
    if mode == "tools":
        if not any("__" in name for name in names):
            raise ValueError("Expected Tool Mode tools named alias__action; the server advertised no connector tools")
        return
    if mode == "code":
        required = {"weavz_search", "weavz_read_api", "weavz_execute"}
        missing = {suffix for suffix in required if not any(name.endswith(suffix) for name in names)}
        if missing:
            raise ValueError(f"Expected Code Mode tools {sorted(required)}; missing {sorted(missing)}")
        return
    raise ValueError("Choose MCP mode tools or code")
