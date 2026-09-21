# Architecture

```text
Codex / Pi
    |
    +-- Agent Skill discovery --> SKILL.md
    |
    +-- MCP / helper script --> local Python runtime
                              |
                              +--> laya-mlx
                                   |
                                   +--> MLX / Apple GPU
```

The Agent Skill explains when Laya is useful and how to interpret its output. The runtime provides deterministic structured access to the local model. The MCP layer lets Codex call it without users writing Python.

## Design principles

1. **Advisory, not authoritative** — Laya suggests routing signals; the coding agent remains responsible for decisions.
2. **Fail open** — a broken model or MCP must never block normal coding-agent work.
3. **Private runtime** — dependencies live in `~/.local/share/laya-router/.venv`.
4. **No shell alias** — never replace the real `codex` binary.
5. **Shared skill path** — `~/.agents/skills` works with Codex and Pi.
6. **Local by default** — after initial checkpoint download, inference stays local.
