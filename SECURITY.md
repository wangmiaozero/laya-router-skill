# Security Policy

Report security issues privately through [GitHub Security Advisories](https://github.com/wangmiaozero/laya-router-skill/security/advisories/new) or to tuziling84@gmail.com.

Laya Router runs as the current user. Its output is advisory and cannot authorize destructive commands, credentials access, production changes, or a final security verdict. Never convert model output into shell commands. The host agent and user retain permission and sandbox decisions.

Inference is local after the first model download. `persist_task_text=false` by default. The router does not log task text or model exception messages, which might contain sensitive input. MCP stdout is reserved for protocol messages.
