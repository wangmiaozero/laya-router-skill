# Laya Router Skill

[简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

Universal, cross-platform local decision routing for AI coding agents, powered by Laya and Laya-MLX.

For ChatGPT Desktop (Codex), Codex CLI, Claude Code, OpenCode, Pi, and other Agent Skills compatible agents. Laya Router becomes available as a local decision capability. An agent invokes it only when its own skill or tool selection policy chooses to; use the CLI or configured MCP tool for an explicit call.

**Version: v0.2.0.** Real MLX, PyTorch and stdio MCP smoke tests passed on an Apple Silicon Mac. Explicit ChatGPT Desktop (Codex), Codex CLI, Claude Code and OpenCode calls were verified. Native Windows/Linux and Intel Mac inference remain unverified.

Laya Router is advisory only. Supported agents can invoke it when their skill or tool selection policy decides it is useful. Explicit invocation results are shown below; implicit invocation is agent-dependent and not guaranteed.

## Compatibility

| Platform | Backend | CI | Real inference |
| --- | --- | --- | --- |
| macOS Apple Silicon | laya-mlx / MLX GPU | Python 3.11/3.12 verified | Verified |
| macOS Apple Silicon (Torch) | upstream Laya / PyTorch MPS + CPU | Python 3.11/3.12 verified | Verified |
| Windows | upstream Laya / PyTorch CPU/CUDA | Python 3.11/3.12 verified | Not yet verified on a native Windows device |
| Linux | upstream Laya / PyTorch CPU/CUDA | Python 3.11/3.12 verified | Not yet verified on a native Linux device |
| Intel macOS | upstream Laya / PyTorch | Architecture covered; no native-device CI | Not verified |

| Client | Skill discovery | Explicit invocation | Implicit invocation | MCP / CLI | Status |
| --- | --- | --- | --- | --- | --- |
| ChatGPT Desktop (Codex) | Verified | Verified: three `laya_decide` calls | Agent-dependent; not guaranteed | MCP verified | Verified |
| Codex CLI | Verified | Verified | Partially verified; agent-dependent | MCP verified | Verified explicit invocation |
| Claude Code | Verified | Verified | Not guaranteed | CLI / Skill verified | Verified explicit invocation |
| OpenCode | Verified | Verified | Not guaranteed | CLI / Skill verified | Verified explicit invocation |
| Pi | Verified | Provider quota blocked full E2E | Not guaranteed | Skill integration verified | Integration verified; full E2E pending |

These are integration mechanisms, not guarantees that an agent calls Laya on every request. Skill discovery and CLI/MCP access depend on each host's settings and permissions. Only Codex MCP registration is automated, under the name `laya-router`. Existing MCP entries named `laya` are left untouched.

The [RC cross-platform CI run](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35574162049) passed all six Ubuntu, Windows and macOS jobs. CI covers packaging, unit tests, compileall, installer dry-run and lightweight health checks; it does not run model inference.

ChatGPT Desktop (Codex) completed explicit E2E tests A, B and C through the MCP tool. The agent made its own final decisions, including a high-risk assessment where the router returned `medium`.

Agent E2E evidence and limitations are recorded in [AGENT_E2E.md](references/AGENT_E2E.md). Decision calls append only timestamp, source, tool, backend, runtime, status, duration and a SHA-256 task hash to the user data directory's `logs/events.jsonl`. Full task text is not logged.

## Install

Python 3.11 or 3.12 is recommended; a private virtual environment is created in the platformdirs user data directory. Nothing is installed into global Python. A checkpoint is downloaded only on the first decision.

macOS / Linux:

```sh
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
python3 scripts/install.py
```

Windows PowerShell:

```powershell
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
py -3 scripts\install.py
```

`--agents auto` selects detected commands. `--agents all` installs all four skill integrations. `--agents codex,claude,opencode,pi` selects specific integrations. `--backend auto|mlx|torch` selects backend; `--no-mcp` skips Codex MCP; `--dry-run` makes no changes; `--force` backs up an existing skill target before replacing it. `--yes` is accepted for automation. Existing unowned integrations are skipped by default.

`--backend` chooses the dependency at installation and is written to a new config. A repeated install preserves an existing `config.json`; edit its `backend` field to change runtime selection. This protects local user settings.

If the installer reports a backend installation failure, inspect the result with the health check. It can still install the core CLI, which returns `status=unavailable` until the backend is available. The installer does not replace `codex`, `claude`, `opencode`, or `pi`.

## Use

```sh
laya-router decide "Refactor this Vue module and inspect risk" --json
laya-router health
laya-router info
laya-router config
laya-router backend
laya-router version
```

The installer creates a user-level `laya-router` launcher when `~/.local/bin` already exists on macOS/Linux, or in its user data `bin` directory on Windows. It prints `PATH status: READY` or `ACTION REQUIRED`; it never edits shell startup files or Windows environment variables. If needed, add `~/.local/bin` to PATH yourself with `export PATH="$HOME/.local/bin:$PATH"`, or call the private venv executable by its full path. `python scripts/decide.py "..."` is a source-checkout helper after installation. A separate CLI process reloads its model; the optional MCP adapter keeps selected checkpoints hot in its long-running process.

The six answers are `task_type`, `complexity` (0 trivial, 1 normal, 2 complex, 3 very complex), `needs_strong_reasoning`, `needs_tools`, `security_sensitive`, and `risk`. Both backends return the same envelope with `status`, `backend`, `runtime`, `model`, `device`, `advisory`, `answers`, `routing`, and `usage`. On failure the result contains `status=unavailable`, `advisory=true`, and `fail_open=true`; the agent continues normally.

The optional MCP adapter requires `mcp>=1,<2`. MCP 2.x is currently unsupported because of tested compatibility issues.

## Advisory behavior

Laya Router may classify a task differently from the final agent judgment. In a destructive-operation analysis, Laya returned `risk=medium` while Codex judged the task high risk and executed no dangerous operation. The agent's security, permission, sandbox and approval policies always take precedence.

Laya Router does not authorize shell commands, approve destructive operations, bypass a sandbox or user approval, replace security review, or replace agent reasoning.

## Scope and safety

Laya is useful for classification, routing, choice, score, `noul` probability, risk signals, and complexity hints. It does not replace code generation, debugging, architecture reasoning, security audits, or final approval. Laya base checkpoints may have limited zero-shot accuracy on some typed-decision workloads. Routing confidence is not a measured probability of correctness. The host agent and user retain all permission, sandbox, and security decisions. No model answer is executed as a shell command.

Inference is local after the first checkpoint download. Task text is not persisted by default. Logs avoid task text and model exception messages. MCP stdout carries only protocol data.

## Check and uninstall

```sh
python3 scripts/healthcheck.py --json
python3 scripts/uninstall.py --all --dry-run
python3 scripts/uninstall.py --all
```

Health check does not download weights; an absent agent is reported as `SKIP`. The ownership manifest limits uninstall to files and Codex MCP entries created by this installer. It does not delete agent configuration directories or the global model cache.

The real checkpoint and stdio MCP checks are marked `integration` and excluded from ordinary `pytest`. After installing a backend and MCP SDK in an isolated venv, run `python -m pytest -m integration`. This can download model weights and needs the selected device. Pull-request CI runs only lightweight tests; a manual workflow dispatch can opt in to model download.

## Development

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest
```

The runtime uses upstream [Laya](https://github.com/NandhaKishorM/laya) and the [Laya-MLX port](https://github.com/mizorewww/laya-mlx). See [architecture](references/ARCHITECTURE.md), [backends](references/BACKENDS.md), [agent integration](references/AGENTS.md), and the [RC validation report](references/RC_VALIDATION.md).

Author: wangmiao · tuziling84@gmail.com · [GitHub](https://github.com/wangmiaozero). Apache-2.0. This is an independent integration.
