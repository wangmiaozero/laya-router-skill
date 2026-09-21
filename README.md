# Laya Router Skill

[简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

Cross-platform local decision routing for AI coding agents, powered by Laya and Laya-MLX.

For ChatGPT Desktop (Codex), Codex CLI, Claude Code, OpenCode, Pi, and other Agent Skills compatible agents. Laya Router becomes available as a local decision capability. An agent invokes it only when its own skill or tool selection policy chooses to; use the CLI for an explicit call.

## Compatibility

| Platform | Backend | Device | Status |
| --- | --- | --- | --- |
| macOS Apple Silicon | laya-mlx | MLX GPU | Implemented; host smoke test pending |
| macOS Intel | upstream laya | CPU / supported MPS | Implemented; host smoke test pending |
| Windows | upstream laya | CPU / CUDA | Implemented; CI configured |
| Linux | upstream laya | CPU / CUDA | Implemented; CI configured |

| Agent | Skill | CLI | MCP |
| --- | --- | --- | --- |
| ChatGPT Desktop (Codex) | Shared Agent Skills path | Local command when shell tools are available | Codex MCP through public CLI, best effort |
| Codex CLI | Shared Agent Skills path | Yes | Public `codex mcp add`, best effort |
| Claude Code | Personal skill path | Yes | Manual setup only |
| OpenCode | Shared compatible path | Yes | Manual setup only |
| Pi | Shared Agent Skills path | Yes | Manual setup only |

These are integration mechanisms, not guarantees that an agent calls Laya on every request. Skill discovery and CLI/MCP access depend on each host's settings and permissions. Only Codex MCP registration is automated.

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

The installed CLI is in the private venv's `bin` directory on macOS/Linux or `Scripts` on Windows. Add that directory to PATH if desired, or call the executable by its full path. `python scripts/decide.py "..."` is a source-checkout helper after dependencies are installed. For long-running hot model instances, use the optional MCP adapter.

The six answers are `task_type`, `complexity` (0 trivial, 1 normal, 2 complex, 3 very complex), `needs_strong_reasoning`, `needs_tools`, `security_sensitive`, and `risk`. Both backends return the same envelope with `status`, `backend`, `runtime`, `model`, `device`, `advisory`, `answers`, `routing`, and `usage`. On failure the result contains `status=unavailable`, `advisory=true`, and `fail_open=true`; the agent continues normally.

## Scope and safety

Laya is useful for classification, routing, choice, score, `noul` probability, risk signals, and complexity hints. It does not replace code generation, debugging, architecture reasoning, security audits, or final approval. Base checkpoints can be inaccurate for some zero-shot typed decisions. The host agent and user retain all permission, sandbox, and security decisions. No model answer is executed as a shell command.

Inference is local after the first checkpoint download. Task text is not persisted by default. Logs avoid task text and model exception messages. MCP stdout carries only protocol data.

## Check and uninstall

```sh
python3 scripts/healthcheck.py --json
python3 scripts/uninstall.py --all --dry-run
python3 scripts/uninstall.py --all
```

Health check does not download weights; an absent agent is reported as `SKIP`. The ownership manifest limits uninstall to files and Codex MCP entries created by this installer. It does not delete agent configuration directories or the global model cache.

## Development

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest
```

The runtime uses upstream [Laya](https://github.com/NandhaKishorM/laya) and the [Laya-MLX port](https://github.com/mizorewww/laya-mlx). See [architecture](references/ARCHITECTURE.md), [backends](references/BACKENDS.md), and [agent integration](references/AGENTS.md).

Author: wangmiao · tuziling84@gmail.com · [GitHub](https://github.com/wangmiaozero). Apache-2.0. This is an independent integration.
