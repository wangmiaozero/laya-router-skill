# Architecture

```text
AI agents (ChatGPT Desktop (Codex), Codex CLI, Claude Code, OpenCode, Pi)
  -> Agent Skill -> laya-router CLI
                  -> optional MCP adapter
                  -> RouterCore -> LayaBackend
                                 -> laya-mlx / MLX (Apple Silicon)
                                 -> upstream laya / PyTorch (other platforms)
```

The CLI is the stable entry point. MCP exposes `laya_decide`, `laya_health`, and `laya_info` over stdio and shares the core. The runtime never executes model output. All errors yield `status=unavailable`, `advisory=true`, and `fail_open=true`. In `backend=auto`, Apple Silicon tries MLX then PyTorch. An explicit backend never silently changes.

The upstream Router handles language and checkpoint selection. Its model instances are lazy and retained in the long-running process, with at most two loaded at once. A separate CLI process has a separate lifetime; use MCP for hot repeated requests.

The Python environment and config live in a platformdirs user data directory. Agent skill links point to a separate copied skill tree. The installer records ownership in `install-manifest.json`; uninstall consults that file before deletion.
