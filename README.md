<p align="center">
  <img src="assets/banner.svg" alt="mcp-doctor — Static Security Scanner, Schema Linter & Token-Budget Auditor for MCP Servers" width="100%">
</p>

<p align="center">
  <a href="https://github.com/RANJITHROSAN17/mcp-doctor/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/RANJITHROSAN17/mcp-doctor/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/RANJITHROSAN17/mcp-doctor/labels/good%20first%20issue"><img alt="Good First Issues" src="https://img.shields.io/github/issues/RANJITHROSAN17/mcp-doctor/good%20first%20issue?color=7057ff&label=good%20first%20issues"></a>
  <a href="https://github.com/RANJITHROSAN17/mcp-doctor/labels/help%20wanted"><img alt="Help Wanted" src="https://img.shields.io/github/issues/RANJITHROSAN17/mcp-doctor/help%20wanted?color=008672"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776ab?logo=python&logoColor=white">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-black"></a>
  <a href="CONTRIBUTING.md"><img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-welcome-10b981"></a>
</p>

<p align="center">
  <b>Audit any Model Context Protocol (MCP) server or AI agent tool manifest in milliseconds — before unsafe tools, broken schemas, or 8,000-token descriptions ship to production.</b>
</p>

---

## Why `mcp-doctor`?

Every MCP server and agent tool registry exposes two invisible failure surfaces:
1. **Security & Reliability Sinks:** LLM-controlled arguments flowing straight into `subprocess.run(..., shell=True)`, unvalidated SSRF `urlopen(url)` calls, or unconfined `open(path, "w")` path traversal.
2. **Context-Window Token Tax & Schema Drift:** Missing descriptions, untyped `Any` parameters, unbounded `limit` / array inputs, and bloated tool docstrings paid on **every single conversation turn**.

`mcp-doctor` inspects Python MCP servers (`FastMCP`, official `mcp` SDK, `@tool` decorators) via pure `ast.parse` (**never executing untrusted code**) alongside MCP `tools/list`, OpenAI, and Anthropic JSON manifests — with **zero external runtime dependencies** on Python 3.11+.

---

## Quickstart (30 Seconds)

```bash
# Run directly with uvx (zero install) or pip:
uvx --from git+https://github.com/RANJITHROSAN17/mcp-doctor.git mcp-doctor scan .

# Or install into your environment:
pip install git+https://github.com/RANJITHROSAN17/mcp-doctor.git
mcp-doctor scan path/to/mcp_server.py
```

### Example Output

```text
==============================================================================
MCP Doctor Report  |  Health Score: 27/100 (F)  |  Tools: 2 across 1 file(s)
Context Footprint: ~102 tokens  |  Errors: 3  Warnings: 4  Info: 1
==============================================================================

[ERROR] MCP001 (missing-tool-description) at examples/vulnerable_server.py:21 [run]
        Tool 'run' has an empty or overly brief description (0 chars; minimum 12 recommended).
[ERROR] MCP008 (ambiguous-or-duplicate-tool-name) at examples/vulnerable_server.py:21 [run]
        Tool name 'run' is overly generic or violates `[a-z][a-z0-9_-]{2,63}`.
[ERROR] MCP005 (dangerous-shell-execution) at examples/vulnerable_server.py:23 [run]
        Tool 'run' invokes dangerous execution sink `subprocess.run(shell=True)` with parameter 'cmd'.
[WARN ] MCP006 (unvalidated-ssrf-sink) at examples/vulnerable_server.py:31 [fetch_and_save_remote_blob]
        Tool 'fetch_and_save_remote_blob' passes parameter 'target_url' into outbound request `urllib.request.urlopen` without visible URL/host validation (potential SSRF).
[WARN ] MCP007 (unconfined-filesystem-access) at examples/vulnerable_server.py:33 [fetch_and_save_remote_blob]
        Tool 'fetch_and_save_remote_blob' passes parameter 'output_path' to `open(write)` without `.resolve()` / base-directory confinement (path traversal risk).
```

### Inspect Context-Window Token Tax

```bash
mcp-doctor token-report examples/
```

---

## Built-in Diagnostic Rules

| Rule ID | Slug | Severity | Category | What It Catches |
| :--- | :--- | :---: | :---: | :--- |
| **`MCP001`** | `missing-tool-description` | `error` | `contract` | Empty or `<12`-char tool description impairing LLM tool routing |
| **`MCP002`** | `excessive-tool-tokens` | `warning` | `tokens` | Single tool schema exceeding token budget (`--max-tokens`, default `250`) |
| **`MCP003`** | `untyped-or-any-parameter` | `warning` | `schema` | Missing type annotation or unconstrained `Any` / bare `dict` / `list` |
| **`MCP004`** | `unbounded-collection-or-limit` | `info` | `schema` | Pagination or array parameter (`limit`, `items`, `list[T]`) with no upper cap |
| **`MCP005`** | `dangerous-shell-execution` | `error` | `security` | `subprocess.*(..., shell=True)`, `os.system`, `eval`, or `exec` in tool body |
| **`MCP006`** | `unvalidated-ssrf-sink` | `warning` | `security` | Outbound HTTP request (`requests`, `httpx`, `urlopen`) on unvalidated URL input |
| **`MCP007`** | `unconfined-filesystem-access` | `warning` | `security` | File read/write/delete on raw input path without `.resolve()` confinement |
| **`MCP008`** | `ambiguous-or-duplicate-tool-name` | `error` | `contract` | Duplicate tool identifiers or generic names (`run`, `do`, `execute`) |

Suppress an intentional finding inline with `# noqa: MCP005` or project-wide in `.mcp-doctor.toml`:

```toml
max-tool-tokens = 250
max-server-tokens = 4000
ignore = ["MCP004"]
exclude = [".venv", "tests/fixtures"]
```

---

## GitHub Action & SARIF Code Scanning

Drop `mcp-doctor` into any repository's `.github/workflows/ci.yml` to get automatic **GitHub Step Summary scorecards** and optional **SARIF v2.1.0** Security tab uploads:

```yaml
- name: Audit MCP Server
  uses: RANJITHROSAN17/mcp-doctor@main
  with:
    path: src/
    fail-on: error
    max-tokens: "250"
    sarif-output: mcp-doctor.sarif
```

---

## Contribute to `mcp-doctor` (Open-Source Friendly!)

`mcp-doctor` is architected specifically for clean, modular community contributions — adding a new lint rule, framework loader (TypeScript MCP SDK, YAML/OpenAPI, live stdio introspection), or output reporter (`--format github`, `--format html`) takes **~50–120 lines of Python**:

- Browse open [**`good first issue`**](https://github.com/RANJITHROSAN17/mcp-doctor/labels/good%20first%20issue) and [**`help wanted`**](https://github.com/RANJITHROSAN17/mcp-doctor/labels/help%20wanted) tasks (automatically curated and replenished by our **Roadmap Bot** as issues close!).
- Read [**`CONTRIBUTING.md`**](CONTRIBUTING.md) and [**`ARCHITECTURE.md`**](ARCHITECTURE.md) for a 10-minute rule walkthrough.

---

## License

MIT © [Ranjith Rosan](https://github.com/RANJITHROSAN17)
