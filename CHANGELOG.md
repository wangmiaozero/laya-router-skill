# Changelog

## 0.2.0

### Added

- Cross-platform Laya Router runtime with automatic backend selection: Laya-MLX on Apple Silicon and upstream Laya/PyTorch on Windows, Linux and Intel macOS.
- Universal CLI, optional MCP adapter, health check and cross-platform installer with safe uninstall.
- ChatGPT Desktop (Codex), Codex CLI, Claude Code, OpenCode and Pi Skill integrations.
- Fail-open behavior, Agent E2E validation and anonymous invocation metadata logging without task text.
- Windows, Linux and macOS CI for Python 3.11 and 3.12.

### Changed

- MCP is an optional adapter rather than the core runtime; Skill discovery spans supported agents.
- Runtime paths are platform-aware, and all Laya decisions are explicitly advisory.
- Compatibility reporting distinguishes discovery, explicit invocation and implicit invocation.

### Fixed

- Pinned MCP SDK to the tested 1.x range due to 2.x compatibility issues.
- Preserved unowned or changed Skill and MCP entries during uninstall; prevented duplicate MCP registration.
- Corrected launcher quoting for paths with spaces and Windows CI behavior.
- Kept MCP stdout free of diagnostic output and preserved user configuration during repeated installation.

## 0.2.0rc2

- Verified explicit Agent calls through Codex CLI MCP and Claude Code/OpenCode Skills.
- Added prompt-free decision call metadata for Agent E2E evidence.
- Preserved changed Skill copies and MCP entries during uninstall.
- Added an Agent E2E report and detailed compatibility matrix.

## 0.2.0rc1

- Real backend and MCP smoke validation on macOS Apple Silicon.
- Private CLI launcher and safer install validation.
