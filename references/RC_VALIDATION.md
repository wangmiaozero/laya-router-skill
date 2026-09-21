# v0.2.0-rc.1 Validation Report

Validation host: macOS 27.0 arm64, Python 3.14.4. Tests used a private venv under a temporary HOME whose path contained spaces. The installed package was `0.2.0rc1`; no packages were installed globally. This report records observed behavior, not a performance benchmark.

## Backend and real model

| Check | Result |
| --- | --- |
| MLX, English checkpoint | `status=ok`, `backend=mlx`, `device=gpu`, six nonempty answers |
| MLX, multilingual checkpoint | Chinese task returned `status=ok`, `model=multilingual`, six nonempty answers |
| upstream Laya/PyTorch MPS | `status=ok`, `backend=torch`, `device=mps`, six nonempty answers |
| upstream Laya/PyTorch CPU | `status=ok`, `backend=torch`, `device=cpu`, six nonempty answers |
| auto fallback | Unit test forces MLX import failure and verifies Torch selection |
| both backends fail | Unit test verifies `status=unavailable`, `fail_open=true` |

Observed model loading: the first English MLX CLI call took about 18 seconds and the first multilingual call about 16 seconds, including Hub fetch. A subsequent English CLI process took about 1 second. `/usr/bin/time` reported roughly 967 MB maximum resident set size and 1.55 GB peak memory footprint for the first English call. Two decisions in the same MCP process took about 1.09 seconds then 0.17 seconds; the backend instance stayed hot. These observations depend on cache, hardware and task and should not be treated as benchmark guarantees.

## CLI and MCP

`version`, `info`, `health`, `backend`, `config`, and `decide` returned exit code 0. All supported JSON variants parsed with `json.loads`; Chinese input worked. stdout contained a single JSON document in JSON mode, while Hub progress and SDK logs went to stderr. Paths with spaces and a separate Chinese source path passed installer dry-run, CLI and MCP tool discovery.

A real MCP client connected over stdio and called `laya_health`, `laya_info`, and `laya_decide`. All calls succeeded after pinning MCP SDK to compatible 1.x. The initial unbounded dependency selected MCP 2.x, whose removed `FastMCP` interface prevented startup; this was a release blocker and is fixed. Disabling the router produced `status=unavailable`, `fail_open=true` on two consecutive real MCP calls without killing the server.

## Agents

| Agent | Observed | Limit |
| --- | --- | --- |
| ChatGPT Desktop (Codex) | App present; public shared Skill and Codex MCP paths checked | Manual UI smoke pending |
| Codex CLI 0.154.0 | Isolated `codex mcp list` and `get` showed the owned `laya-router` entry; direct MCP client called all tools | Model-driven tool selection pending |
| Claude Code 2.1.267 | Personal Skill symlink installed; normal isolated command reached login requirement | Authenticated E2E pending; MCP manual |
| OpenCode 1.18.31 | `opencode debug skill` listed `laya-router` from shared path | Model-driven invocation pending; MCP manual |
| Pi 0.85.1 | Shared Skill symlink and CLI helper installed | Isolated explicit run stopped for missing provider API key; MCP optional |

## Installer and uninstall

First install, repeated install, agent-specific installs, `--force`, and `--dry-run` all completed in the isolated HOME. The owned Skill entries and MCP entry remained singular, the existing config was preserved, and no backup files accumulated. The user-level launcher worked from PATH when the test bin directory was present. A separate Chinese source path passed dry-run, CLI version and stdio MCP discovery.

Real `uninstall.py --all --dry-run` listed only owned Skill links, MCP entry, launcher, venv, config and copied source. Real uninstall removed them and left six unrelated sentinel files in Codex, Claude, OpenCode, Pi, other Skills and Hugging Face cache locations. `codex mcp list` then reported no configured servers in the isolated CODEX_HOME.

## Tests and CI

Ordinary local `pytest`: 14 passed, 2 integration tests deselected. Explicit `pytest -m integration`: 2 passed. `compileall`, installer dry-run, lightweight health check and `git diff --check` passed. Ordinary CI has six jobs (Ubuntu, Windows, macOS; Python 3.11 and 3.12) and does not download model weights. Manual `workflow_dispatch` can opt in to a real checkpoint test; `download_model` defaults to false.

The [latest GitHub Actions run](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35574162049) completed successfully: all six Ubuntu, Windows and macOS jobs passed on Python 3.11 and 3.12. An earlier run passed Ubuntu and macOS but failed both Windows jobs because a test used host `Path` for both POSIX and Windows example paths. The test now uses explicit `PurePosixPath` and `PureWindowsPath`.

## Release assessment

No defined RC release blockers remain after the MCP SDK pin, canonical symlink check and Windows CI test correction. The code is ready for a `v0.2.0-rc.1` tag; this validation did not create a tag or merge main. Remaining native-client E2E tests are documented as pending. Intel Mac, Windows CUDA and Linux real inference were not tested on this host. Base checkpoint confidence is advisory and is not calibrated accuracy.
