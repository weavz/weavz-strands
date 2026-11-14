from __future__ import annotations

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from connection import validate_catalog, validate_live_connection


@pytest.mark.parametrize("url,token", [
    ("https://tenant.example/mcp", "mcp_example-token"),
    ("http://127.0.0.1:8080/mcp", "mcp_example-token"),
    ("http://[::1]:8080/mcp", "mcp_example-token"),
    ("http://localhost:8080/mcp", "mcp_example-token"),
])
def test_accepts_secure_or_loopback_connection(url: str, token: str) -> None:
    assert validate_live_connection(url, token) == (url, token)


@pytest.mark.parametrize("url,token", [
    ("", "mcp_example-token"),
    ("https://tenant.example/mcp", ""),
    ("https://tenant.example/mcp", "wvz_example-rest-key"),
    ("https://tenant.example/mcp", "mcp_bad token"),
    ("https://tenant.example/mcp", "mcp_bad\ntoken"),
    ("http://tenant.example/mcp", "mcp_example-token"),
    ("ftp://localhost/mcp", "mcp_example-token"),
    ("file://localhost/mcp", "mcp_example-token"),
    ("https://user:secret@tenant.example/mcp", "mcp_example-token"),
    ("https://tenant.example/mcp?token=secret", "mcp_example-token"),
    ("https://tenant.example/mcp?", "mcp_example-token"),
    ("https://tenant.example/mcp#secret", "mcp_example-token"),
    ("https://tenant.example/mcp#", "mcp_example-token"),
    ("https://tenant.example/mcp/weavz", "mcp_example-token"),
    ("https://tenant.example:bad/mcp", "mcp_example-token"),
])
def test_rejects_unsafe_or_invalid_connection(url: str, token: str) -> None:
    with pytest.raises(ValueError):
        validate_live_connection(url, token)


def test_accepts_expected_mode_catalogs() -> None:
    validate_catalog("tools", {"office_slack__search_messages"})
    validate_catalog("tools", {"weavz_demo__lookup_record"})
    validate_catalog("code", {"weavz_search", "weavz_read_api", "weavz_execute"})
    validate_catalog("code", {"ns_weavz_search", "ns_weavz_read_api", "ns_weavz_execute"})


@pytest.mark.parametrize("mode,names", [
    ("tools", {"weavz_search", "weavz_read_api", "weavz_execute"}),
    ("tools", set()),
    ("code", {"demo__lookup_record"}),
    ("code", {"weavz_search", "weavz_execute"}),
])
def test_rejects_mode_catalog_mismatch(mode: str, names: set[str]) -> None:
    with pytest.raises(ValueError):
        validate_catalog(mode, names)
