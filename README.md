# Laya Router Skill

[简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

Cross-platform local decision routing for AI coding agents, powered by Laya and Laya-MLX.

For ChatGPT Desktop (Codex), Codex CLI, Claude Code, OpenCode, Pi, and other Agent Skills compatible agents. Laya Router becomes available as a local decision capability. An agent invokes it only when its own skill or tool selection policy chooses to; use the CLI for an explicit call.

**Release status: v0.2.0-rc.2.** The core runtime passed real MLX, PyTorch and stdio MCP smoke tests on an Apple Silicon Mac. Explicit Codex CLI, Claude Code and OpenCode calls were also verified. Desktop UI E2E and non-macOS runtime inference remain pending where noted below.

## Compatibility

| Platform | Backend | CI | Real inference |
| --- | --- | --- | --- |
| macOS Apple Silicon | laya-mlx GPU; upstream laya CPU/MPS | Python 3.11/3.12 verified | Verified for both backends on macOS arm64 |
| macOS Intel | upstream laya CPU/MPS | Pending | E2E pending |
| Windows | upstream laya CPU/CUDA | Python 3.11/3.12 verified | E2E pending |
| Linux | upstream laya CPU/CUDA | Python 3.11/3.12 verified | E2E pending |

| Client | Skill discovery | Explicit invocation | Implicit invocation | MCP | Status |
| --- | --- | --- | --- | --- | --- |
| ChatGPT Desktop (Codex) | Verified in this session | CLI helper verified | E2E pending | Registered; UI E2E pending | Implemented / Manual UI E2E Pending |
| Codex CLI | Verified | `laya_decide` and MLX verified | Skill selected; real inference not verified | Verified with automatic approval | Verified explicit E2E |
| Claude Code | Verified | Skill to CLI to MLX verified | Skill selected; real inference not verified | Not configured | Verified explicit E2E |
| OpenCode | Verified | Skill to CLI to MLX verified | Skill selected; real inference not verified | Not configured | Verified explicit E2E |
| Pi | Verified | E2E pending: provider quota | E2E pending | Not configured | E2E Pending |

These are integration mechanisms, not guarantees that an agent calls Laya on every request. Skill discovery and CLI/MCP access depend on each host's settings and permissions. Only Codex MCP registration is automated, under the name `laya-router`. Existing MCP entries named `laya` are left untouched.

The [RC cross-platform CI run](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35574162049) passed all six Ubuntu, Windows and macOS jobs. CI covers packaging, unit tests, compileall, installer dry-run and lightweight health checks; it does not run model inference.

For a manual ChatGPT Desktop (Codex) check: restart the app, open Codex, confirm the Laya Router Skill is discoverable, submit a coding task that benefits from classification, and confirm the Skill or MCP reports no error. Record whether the agent actually invoked it; automatic selection is not guaranteed.

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
