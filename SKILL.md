---
name: laya-router
description: Use local Laya-MLX on Apple Silicon for fast task triage, complexity scoring, escalation hints, tool-use hints, and lightweight risk classification before or during coding-agent work. Use when deciding how to route a task, whether stronger reasoning is warranted, whether tools are likely needed, or when a cheap local structured decision can avoid unnecessary frontier-model reasoning. Do not use Laya as a replacement for coding, debugging, architecture reasoning, security review, or final judgment.
license: Apache-2.0
compatibility: macOS 14+ on Apple Silicon, Python 3.11+, Codex or Pi with Agent Skills support.
metadata:
  author: wangmiao
  email: tuziling84@gmail.com
  url: https://github.com/wangmiaozero
  runtime: laya-mlx
  model: aac6fef/laya-multilingual-mlx
---

# Laya Router

Use this skill to make **small, structured local decisions** with Laya before spending expensive reasoning on routine routing questions.

## What Laya is for

Good uses:

- classify a task type
- estimate task complexity
- estimate whether strong reasoning is warranted
- estimate whether tools are likely required
- flag security-sensitive tasks for extra review
- choose among a small set of agent or workflow routes

Do **not** treat Laya as authoritative. It is an advisory decision layer.

Do not delegate these tasks entirely to Laya:

- writing or editing production code
- debugging root causes
- architecture design
- security conclusions
- destructive-operation approval
- final user-facing decisions

## First-time setup

From the skill directory, run:

```bash
./scripts/install.sh
```

This installs a private Python virtual environment under:

```text
~/.local/share/laya-router/
```

It does not install Python packages globally.

## Health check

```bash
./scripts/healthcheck.sh
```

## Direct decision call

```bash
./scripts/decide.sh "Refactor this Vue module to React and review risky changes"
```

The command returns JSON.

## Codex integration

The installer attempts to register the local MCP server as `laya` using the installed Codex CLI when supported.

Verify with:

```bash
codex mcp list
```

If the MCP server is available, prefer the `laya_decide` tool for task triage instead of shelling out to the helper script.

## Pi integration

Pi discovers Agent Skills from `~/.agents/skills/`. Install this repository there or symlink it there.

Pi can also use the direct helper scripts from this skill. If your Pi setup has MCP support configured, you may register the same runtime there separately.

## Decision policy

When the user's task materially benefits from routing, send only the task summary needed for classification to Laya.

Interpret results conservatively:

- `simple` / low complexity: proceed normally; do not add ceremony.
- `complex` or `very_complex`: use stronger reasoning if available.
- `security_sensitive=true` or `risk=high`: perform normal agent security checks; never treat Laya as the sole gate.
- low confidence: ignore the suggestion and reason normally.

If Laya is unavailable, **fail open** and continue with the coding agent normally.

## Privacy

Inference is local after model download. Do not send secrets or credentials into logs. The runtime writes only operational logs by default and does not persist task text unless explicitly enabled in config.
