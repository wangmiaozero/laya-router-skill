---
name: laya-router
description: Cross-platform local decision routing for AI coding agents using Laya and Laya-MLX. Use for fast task classification, complexity estimation, model escalation hints, tool-use routing, and lightweight risk assessment. Advisory only.
license: Apache-2.0
compatibility: Cross-platform Python 3.11+ runtime. Apple Silicon uses Laya-MLX when available; other supported platforms use upstream Laya and PyTorch.
metadata:
  author: wangmiao
  email: tuziling84@gmail.com
  url: https://github.com/wangmiaozero/laya-router-skill
---

# Laya Router

Use this skill when a short structured decision would help route a coding task. Summarize only the task details needed for classification. Never include secrets.

Call `python scripts/decide.py "task summary" --json` from this skill directory through a local shell tool. The helper uses the private runtime Python when installed. If `laya-router` is on PATH, `laya-router decide "task summary" --json` is equivalent. If the optional `laya_decide` MCP tool is available, it returns the same protocol.

The result is advisory. It can suggest task type, complexity, reasoning depth, tool use, security sensitivity, and risk. It cannot approve commands, deny work, perform a security audit, or replace coding and debugging. Follow the host agent's permission and sandbox policy. If the router returns `status=unavailable`, continue normal work.

Run `laya-router info` or `python scripts/healthcheck.py` to inspect availability without downloading a checkpoint. Model weights load on the first actual decision. Local inference follows the initial checkpoint download. Task text is not persisted by default.
