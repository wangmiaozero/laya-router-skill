# laya-router-skill

English | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

Local Laya-MLX decision routing for Codex and Pi on Apple Silicon.

`laya-router-skill` packages a reusable **Agent Skill** plus a small local MCP runtime. It uses [laya-mlx](https://github.com/mizorewww/laya-mlx) for fast structured decisions such as task classification, complexity scoring, escalation hints, tool-use hints, and lightweight execution-risk signals.

It does **not** replace GPT, Codex, Pi, code review, or security judgment.

## Why

Coding agents often spend frontier-model reasoning on small routing questions:

- Is this task trivial or complex?
- Is stronger reasoning warranted?
- Is this primarily frontend, backend, architecture, or security work?
- Are tools likely needed?
- Is the requested operation unusually risky?

Laya can answer constrained typed questions locally on Apple Silicon. This project turns that capability into an agent-friendly reusable package.

## Requirements

- Apple Silicon Mac (`arm64`)
- macOS 14+
- Python 3.11+
- Codex and/or Pi

## Install

```bash
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
./scripts/install.sh
```

The installer:

1. creates `~/.local/share/laya-router/.venv`
2. installs `laya-mlx` and the MCP Python SDK
3. installs the skill into `~/.agents/skills/laya-router`
4. best-effort registers a Codex MCP server named `laya`

No global Python packages are installed.

## Install with Codex

Copy this into Codex:

```text
Install and set up https://github.com/wangmiaozero/laya-router-skill on this Apple Silicon Mac.

Do all of the following:
1. Require macOS arm64 and Python 3.11+. Stop if this machine does not match.
2. Clone the repo if it is not already checked out:
   git clone https://github.com/wangmiaozero/laya-router-skill.git
   cd laya-router-skill
3. Run ./scripts/install.sh
4. Run ./scripts/healthcheck.sh
5. If Codex MCP registration failed, register it with:
   codex mcp add laya -- "$HOME/.local/share/laya-router/.venv/bin/python" "$HOME/.local/share/laya-router/server.py" --mcp
6. Verify with: codex mcp list
7. Summarize skill path, runtime path, healthcheck status, and MCP status.

Do not install Python packages globally. If Laya, MLX, the model, or MCP is unavailable, fail open and report the error; do not block normal Codex work. After setup, use this skill for local task triage via the laya MCP tool laya_decide, or ./scripts/decide.sh.
```

## Normal usage

Use Codex normally:

```bash
codex
```

Or Pi normally:

```bash
pi
```

The skill is discoverable through the shared Agent Skills path. Codex can also call the registered local `laya` MCP server.

## Explicit use

Direct local decision:

```bash
./scripts/decide.sh "Refactor this Vue module to React and inspect risky changes"
```

Pi can explicitly load the skill with `/skill:laya-router` when skill commands are enabled.

## Health check

```bash
./scripts/healthcheck.sh
```

## Configuration

Runtime configuration lives at:

```text
~/.local/share/laya-router/config.json
```

Default model:

```text
aac6fef/laya-multilingual-mlx
```

## Fail-open behavior

If Laya, MLX, the model, or MCP is unavailable, the router returns an unavailable/fail-open result. The coding agent should continue normally.

## Uninstall

```bash
./scripts/uninstall.sh
```

This removes the runtime and the installed skill symlink, but not your repository checkout or Codex itself.

## Project structure

```text
laya-router-skill/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── README.zh-TW.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── icon.svg
├── runtime/
│   └── server.py
├── scripts/
│   ├── install.sh
│   ├── decide.sh
│   ├── healthcheck.sh
│   └── uninstall.sh
├── references/
│   └── ARCHITECTURE.md
└── .github/
    └── workflows/
        └── shellcheck.yml
```

## Security

Agent Skills and MCP servers can execute code with user permissions. Review source before installation. Do not use the router as the sole approval gate for destructive or security-sensitive operations.

## Upstream

- Laya: `convaiinnovations/laya`
- MLX port: `mizorewww/laya-mlx`

This project is an independent integration and is not affiliated with Convai Innovations, OpenAI, or the laya-mlx maintainer.

## Author

- wangmiao — tuziling84@gmail.com
- GitHub: https://github.com/wangmiaozero

## License

Apache-2.0.
