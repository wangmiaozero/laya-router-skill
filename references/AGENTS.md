# Agent integrations

Official discovery paths checked in September 2026:

- Codex CLI and ChatGPT Desktop (Codex): `~/.agents/skills/<name>/SKILL.md`; Codex CLI also supports `codex mcp add`.
- Claude Code: `~/.claude/skills/<name>/SKILL.md`. Its `/laya-router` skill command is an explicit invocation.
- OpenCode: `~/.agents/skills/<name>/SKILL.md` is supported as a compatibility location.
- Pi: `~/.agents/skills/<name>/SKILL.md`; `/skill:laya-router` explicitly loads it when skill commands are enabled.

The installer installs shared skill discovery for Codex, OpenCode, and Pi, and a separate Claude Code link. Only Codex MCP auto-registration is implemented and only if its public CLI is available. Other agents can use the universal CLI; MCP registration for them is manual and depends on the installed agent version.

Sources: [OpenAI Skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code Skills](https://code.claude.com/docs/en/skills), [OpenCode Skills](https://opencode.ai/docs/skills), [Pi Skills](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md).
