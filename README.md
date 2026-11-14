# Strands Agents MCP integration examples with Weavz

<!-- weavz:discovery:start -->

Connect Strands Agents to Slack, Gmail, GitHub and Google Calendar through a remote Weavz Model Context Protocol (MCP) server. Use the native MCP adapter, then try the app setup recipes with your configured connections.

App setup recipes:

- [Slack MCP with Strands Agents Python](docs/app-recipes.md#slack-mcp-with-strands-agents-python)
- [Gmail MCP with Strands Agents Python](docs/app-recipes.md#gmail-mcp-with-strands-agents-python)
- [GitHub MCP with Strands Agents Python](docs/app-recipes.md#github-mcp-with-strands-agents-python)
- [Google Calendar MCP with Strands Agents Python](docs/app-recipes.md#google-calendar-mcp-with-strands-agents-python)

The framework consumes app tools from your configured Weavz MCP server. App recipes require your own app connections; automated checks use synthetic records.

[MCP app and framework directory](https://github.com/weavz/mcp-examples/blob/main/docs/integrations.md) · [All examples](https://github.com/weavz/mcp-examples) · [Weavz MCP guide](https://weavz.io/docs/guides/agent-framework-examples)

<!-- weavz:discovery:end -->

Uses Strands' native MCP client with Streamable HTTP and bearer authorization. Configure a custom Weavz MCP server in Tool Mode or Code Mode first. `WEAVZ_MCP_MODE` validates its advertised tools; it cannot change a remote server setting.

Requirements: Python 3.11 or 3.12, uv, and a custom MCP endpoint plus MCP access token. Do not use a Weavz REST API key. The personal `https://platform.weavz.io/mcp/weavz` endpoint uses OAuth.

## Local fixture

```sh
uv sync --locked
uv run python main.py --fixture --mode tools
uv run python main.py --fixture --mode code
uv run pytest
```

The fixture is a separate, bearer-protected MCP SDK server on loopback with synthetic data. These checks do not use a model or live Weavz.

## Weavz and optional model

Copy `.env.example` to `.env` and set the endpoint/token from your custom setup. `uv run --env-file .env python main.py --mode tools` or `--mode code` discovers the live server's actual tools. For a live agent run, connect an app containing records for your task, set `WEAVZ_MODEL` to a Bedrock model id supported by your AWS account and configure AWS credentials, then run `uv run --env-file .env python main.py --mode tools --prompt "Find the latest record matching the task you connected"`.
