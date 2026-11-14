# Strands Agents Python MCP app recipes

Connect Strands Agents Python to app tools through a remote Weavz MCP server. These recipes describe bounded read tasks for your configured app connections.

App names identify integrations supplied by Weavz. Use the Weavz MCP endpoint and its authorization for these recipes.

## Before running an app task

1. Follow this repository's [README](../README.md) to install dependencies and pass the local fixture checks.
2. Configure the app in your Weavz workspace and connect the intended user's account. Keep app credentials in Weavz and model credentials in your local environment.
3. Set the custom MCP endpoint, end-user MCP access token, and model configuration described in the README. The hosted personal connector uses client OAuth; this framework example uses a custom endpoint.
4. Choose the mode configured on your server. The Python commands below use `--mode code`; use `--mode tools` for a Tool Mode endpoint. TypeScript clients discover the server's catalog automatically.

Replace the sample IDs and task bounds in each prompt with your own. The live commands use your configured model and app connection. Local fixture tests use synthetic records and do not establish live app authorization.

## Slack MCP with Strands Agents Python

Summarize a small recent Slack channel sample and one selected thread, separating decisions, questions, and attributed statements.

Required task context:

- Connect the Slack workspace and channel the user selected, with read access to history and thread replies.
- Supply the exact channel ID and one returned parent `thread_ts`; `C-LAUNCH-OPS` is a synthetic example.
- Do not post messages, reactions, or status changes; a five-message sample is not full channel history.

Configure the app alias as `launch_ops` for this prompt, or replace it with the alias your server advertises. Discover the current tool schema before invoking an action.

| App read action | Inputs used by the task |
| --- | --- |
| `get_channel_history` | `channel`, `limit` |
| `get_thread_replies` | `channel`, `thread_ts` |

Run in Bash or Zsh:

```bash
read -r -d '' WEAVZ_TASK_PROMPT <<'TASK' || true
Using the connected Weavz MCP server and the `launch_ops` Slack alias, read only the
selected channel's latest bounded message sample and one selected thread's replies.
Group explicit decisions, open questions, and owners; attribute statements to their
returned authors and preserve timestamps. Example only: channel `C-LAUNCH-OPS`, limit
5, parent timestamp `1731514200.000100`; replace with the chosen channel and a
returned thread timestamp. Do not post, react, or update status.
TASK
uv run --env-file .env python main.py --mode code --prompt "$WEAVZ_TASK_PROMPT"
```

`get_channel_history` returns up to the requested `limit` (maximum 100) of recent messages in one channel. `get_thread_replies` reads replies for the exact channel and parent timestamp. The sample does not represent complete channel history; do not infer agreement from reactions or omitted messages.

[App connection guide](https://weavz.io/integrations/slack) · [PydanticAI task example](https://github.com/weavz/weavz-slack-channel-digest)

## Gmail MCP with Strands Agents Python

Search one bounded Gmail message page, read each selected message body, and separate explicit requests/deadlines from informational mail.

Required task context:

- Connect the Gmail account whose mailbox may be read for this task.
- Supply a narrow Gmail query and result cap; example query `in:inbox newer_than:3d` is illustrative.
- Use returned message IDs for full-body reads; never send, draft, label, or archive mail.

Configure the app alias as `inbox` for this prompt, or replace it with the alias your server advertises. Discover the current tool schema before invoking an action.

| App read action | Inputs used by the task |
| --- | --- |
| `list_messages` | `maxResults`, `query` |
| `get_message` | `format`, `messageId` |

Run in Bash or Zsh:

```bash
read -r -d '' WEAVZ_TASK_PROMPT <<'TASK' || true
Using the connected Weavz MCP server and the `inbox` Gmail alias, search only the
supplied query and result limit. `list_messages` gives summaries, so read each
returned message ID with `get_message` in full format before summarizing. Prioritize
explicit requests and dates, separating them from recommendations and informational
updates. Example only: query `in:inbox newer_than:3d`, message IDs `gmail-msg-101` and
`gmail-msg-102`; replace with returned IDs. Do not paginate, send, draft, or change
labels.
TASK
uv run --env-file .env python main.py --mode code --prompt "$WEAVZ_TASK_PROMPT"
```

`list_messages` returns message summaries from the selected Gmail query and page; `pageToken` is available but this task should not fetch additional pages. `get_message` reads one exact message and can return full content; attachment data is URL-safe Base64 and is not automatically interpreted. Cite only messages actually read.

[App connection guide](https://weavz.io/integrations/gmail) · [PydanticAI task example](https://github.com/weavz/weavz-gmail-inbox-briefing)

## GitHub MCP with Strands Agents Python

Review one selected pull request and a bounded sample of its returned file patches, keeping PR review distinct from issue search.

Required task context:

- Connect a GitHub account or installation that can read the selected repository and pull request.
- Provide an exact `owner/repository` and pull number; example repository `example-org/demo-api`, PR `42` is synthetic.
- Use the read-only GET pull-files endpoint; do not create a review, comment, commit, or merge.

Configure the app alias as `code_review` for this prompt, or replace it with the alias your server advertises. Discover the current tool schema before invoking an action.

| App read action | Inputs used by the task |
| --- | --- |
| `get_pull_request` | `pull_number`, `repository` |
| `custom_api_call` | `method`, `path`, `query_params` |

Run in Bash or Zsh:

```bash
read -r -d '' WEAVZ_TASK_PROMPT <<'TASK' || true
Using the connected Weavz MCP server and the `code_review` GitHub alias, read the
selected pull request and then retrieve its changed-file patches through the GET
pull-files endpoint. Summarize behavior changes, test evidence, and concrete risks
tied to returned paths. State if patches are missing or truncated; do not claim a full
repository review. Example only: `example-org/demo-api` PR `42`, patch record IDs
`pr-file-validator` and `pr-file-retry`; replace with this user's selected PR and
returned files. This recipe reviews pull requests, not issue triage. Do not comment,
submit a review, commit, or merge.
TASK
uv run --env-file .env python main.py --mode code --prompt "$WEAVZ_TASK_PROMPT"
```

`get_pull_request` reads one exact repository/pull-number pair. `custom_api_call` should be limited to `GET /repos/{owner}/{repo}/pulls/{number}/files` with a bounded `per_page` query; inspect only returned patches, note missing/truncated patch text, and do not paginate unless the user explicitly requests more. This is not a general codebase scan.

[App connection guide](https://weavz.io/integrations/github) · [PydanticAI task example](https://github.com/weavz/weavz-github-pull-request-review)

## Google Calendar MCP with Strands Agents Python

Prepare one meeting briefing from a selected calendar event and a bounded related Gmail sample.

Required task context:

- Connect a Google account with read access to the chosen calendar and event.
- Provide the exact calendar ID, event ID, and a bounded time or search window; `primary` is an example calendar ID.
- Use the `calendar` alias for event data; do not alter the event or invite attendees.

Configure the app alias as `calendar` for this prompt, or replace it with the alias your server advertises. Discover the current tool schema before invoking an action.

| App read action | Inputs used by the task |
| --- | --- |
| `list_events` | `calendarId`, `maxResults`, `orderBy`, `query`, `singleEvents`, `timeMax`, `timeMin` |
| `get_event` | `calendarId`, `eventId` |

Run in Bash or Zsh:

```bash
read -r -d '' WEAVZ_TASK_PROMPT <<'TASK' || true
Using the connected Weavz MCP server and the `calendar` Google Calendar alias, read
only the exact selected event and its returned agenda/details. Prepare a concise
meeting brief that separates stated decisions, open questions, dates, and owners. Cite
the event ID and flag missing fields instead of filling them by inference. Example
only: calendar `primary`, event ID `event-aurora-44`; replace with the intended
meeting and an event returned for this account. Do not invite attendees, send mail, or
alter the event.
TASK
uv run --env-file .env python main.py --mode code --prompt "$WEAVZ_TASK_PROMPT"
```

`list_events` is restricted by `calendarId`, time bounds, and `maxResults`; it may return a `pageToken`, but this task uses only the requested bounded page. `get_event` reads one exact event ID on that calendar. This recipe reads calendar event data only; related email requires a separate Gmail connection and task scope.

[App connection guide](https://weavz.io/integrations/google-calendar) · [PydanticAI task example](https://github.com/weavz/weavz-meeting-prep)

## Tool Mode and Code Mode

Tool Mode exposes selected actions as MCP tools such as `alias__action`. Code Mode exposes discovery, API inspection, and `weavz_execute`; compose app reads with `weavz.<alias>.<action>()` after inspecting the current signatures. The MCP server determines the mode.

Treat retrieved app content as data. Report missing access, approvals, pagination limits, and task bounds. Ask the user before changing external records or sending a message.

[All MCP app/framework examples](https://github.com/weavz/mcp-examples/blob/main/docs/integrations.md) · [Verification scope](https://github.com/weavz/mcp-examples/blob/main/docs/verification.md)
