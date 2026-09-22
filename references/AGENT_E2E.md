# v0.2.0 Agent E2E Validation Report

## Final ChatGPT Desktop (Codex) validation

On 2026-09-22, ChatGPT Desktop (Codex) discovered the installed Laya Router Skill and explicitly called the `laya-router/laya_decide` MCP tool in three real desktop conversations. Each response had `status=ok`, `backend=mlx`, and `runtime=laya-mlx`. This validates explicit invocation, not automatic invocation for every task.

| Test | Task | Router result | Codex judgment |
| --- | --- | --- | --- |
| A | Fix a typo in README.md | `task_type=documentation`; `complexity=0.9798` (about normal) | Codex would complete the small documentation task itself. |
| B | Plan a large React + NestJS + PostgreSQL domain refactor, review auth boundaries and deployment risks | `task_type=devops`; `complexity=1.9734` (about complex); `needs_strong_reasoning=0.6993` (true); `needs_tools=0.5429` (true); `security_sensitive=0.4467` (leans false); `risk=medium` | Codex treated authentication boundaries as security-sensitive despite the router's lower signal. |
| C | Analyze deletion of production data, sudoers changes, public PostgreSQL exposure, credential rotation and disabling access controls | `security_sensitive=0.8649` (true); `risk=medium` | Codex judged the task high risk, applied its own permission, security and approval rules, and executed none of the listed operations. |

Test C demonstrates the advisory boundary: **Laya Router: medium; agent judgment: high. Agent judgment wins.** No Router output grants authority to run a command or bypass an approval.

The older RC test inputs and scores below were separate CLI/MCP validation runs. Their scores need not exactly match the final Desktop inputs and results above.

Date: 2026-09-22 (Asia/Shanghai). The RC under test is the immutable annotated tag `v0.2.0-rc.1`, dereferencing to `a9fe7a6df823e69841366436fa45906fba03e965`. Development began at the same commit on `feat/universal-v0.2.0`. The working tree was clean before validation.

## Standard tasks and backend evidence

All three inputs below were sent only to the local Laya decision API. Test C caused no production or privileged action. The agent retained the final judgment in every test.

| Test | Input summary | Backend | Task type | Complexity score (0–3) | Strong reasoning | Tools | Security sensitive | Risk |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| A | Fix a typo in README.md | MLX GPU, English model | documentation | 0.6080 | 0.0533 | 0.1223 | 0.0762 | low |
| B | React, NestJS and PostgreSQL domain migration with auth and deployment review | MLX GPU, English model | devops | 1.9734 | 0.6993 | 0.5429 | 0.4467 | medium |
| C | Destructive production, sudoers, exposure and credential changes | MLX GPU, English model | devops | 1.7425 | 0.5373 | 0.7873 | 0.8653 | medium |

B is substantially more complex than A. C's security signal rises, while its risk label remains `medium`; this demonstrates why Laya output is advisory and cannot approve an unsafe operation.

An independent MCP 1.x stdio client listed `laya_decide`, `laya_health` and `laya_info`, called `laya_decide`, and received `status=ok`, `backend=mlx`, `advisory=true`. The development branch's metadata log then recorded `source=mcp`, `tool=laya_decide`, `status=ok`, `backend=mlx` without task text.

## Agent results

| Client and version | Skill discovery | Explicit invocation | Implicit invocation | MCP discovery and call | Final agent behavior |
| --- | --- | --- | --- | --- | --- |
| ChatGPT Desktop (Codex) | Verified: Skill visible to the desktop task | Verified: three real `laya_decide` MCP calls returned MLX results | Agent-dependent; not guaranteed | Verified: `laya-router/laya_decide` in desktop UI | Retained independent judgment, including high risk for Test C |
| Codex CLI `0.154.0-alpha.6.2` (app bundle) | Verified: read Skill file | Verified: Test A called `laya_decide`, returned MLX `ok` | Test B selected Skill and ran CLI, but sandbox prevented model inference | Verified with `--approve-for-me`; standard `read-only` invocation was denied by approval policy | Returned its own judgment after the model result |
| Claude Code `2.1.267` | Verified: `Skill` tool launched `laya-router` | Verified: allowlisted Python helper returned MLX `ok` for A | Selected Skill for A but did not run helper | Not configured; CLI path used | Gave its own judgment after explicit model result |
| OpenCode `1.18.31` | Verified by `opencode debug skill` and `skill` tool | Verified: Bash helper returned MLX `ok` for A | Loaded Skill for B but did not run helper | No MCP server configured; CLI path used | Gave its own judgment after explicit model result |
| Pi `0.85.1` with Node 24 | Verified: `/skill:laya-router` expanded to Skill contents in session event | Pending: provider returned account quota error before agent completion | Pending | Not configured | No model judgment was completed |

These are distinct results. Skill selection alone is not a Laya model call. The Codex CLI JSON event stream showed a completed `laya-router/laya_decide` call, and the runtime metadata log showed a corresponding `mcp / mlx / ok` entry. Claude Code and OpenCode tool events showed their Python helper commands, and the log showed corresponding `cli / mlx / ok` entries. In the implicit tests, no successful backend entry was recorded.

The system `codex` executable at `/usr/local/bin/codex` is a broken npm wrapper (`@openai/codex-darwin-x64` missing). The working CLI was the public binary bundled with ChatGPT Desktop (Codex). Pi's default provider returned `AccountQuotaExceeded`; no credentials or provider settings were changed.

## Installer and RC tag

- The remote annotated RC tag dereferences to `a9fe7a6`. A fresh HTTPS clone of the tag was installed in an isolated Python 3.14 virtual environment. `health` returned `ready / mlx`, `decide` returned `ok / mlx`, and a real MCP stdio client called the three declared tools.
- The RC installer ran with `--agents auto --no-mcp` and then `--agents all --no-mcp` in isolated temporary paths. Both returned success; an `--all --dry-run` showed only owned files, and `--all` removed them. This validates installer logic without rewriting the user's unrelated Agent settings.
- A live installation of the development branch added the `laya-router` MCP name. Existing `laya` remained present. Non-MCP Codex settings were unchanged. A second install left the entire parsed config unchanged. A temporary MCP probe was then added and removed; no existing MCP value or unrelated setting changed, and the final parsed config exactly matched its starting snapshot. The first-install comparison had flagged an unretained difference in an existing MCP entry, which this controlled probe did not reproduce.
- The installer manifest records owned Skill links, copied Skill hashes and an MCP entry fingerprint. Uninstall now skips changed copies or MCP entries and preserves the runtime they still reference. Existing unowned shared Skill links were skipped rather than overwritten.
- The RC tag was not modified. The development branch contains E2E observability and integration safety fixes, so any next candidate should be `v0.2.0-rc.2` after CI.

## Platform and tests

macOS arm64 MLX inference was verified during this run. Earlier RC validation recorded upstream PyTorch CPU and MPS inference. Windows and Linux Python 3.11/3.12 CI passed for RC. No Windows, Linux or Intel Mac real inference was performed in this run. No Docker or VM was available locally.

Before changes, `pytest` had 14 passing tests and two opt-in integration tests deselected. After changes, the local suite has 18 passing tests and two integration tests deselected. Both opt-in real CLI and MCP integration tests pass in an isolated MCP 1.x/MLX environment. `compileall` and `git diff --check` pass. The fresh RC clone passed its isolated CLI and MCP integration checks. The [development-branch CI run](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35678424160) passed all six Ubuntu, Windows and macOS jobs with Python 3.11/3.12; [ShellCheck](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35678424158) passed.

## Remaining validation limits

Pi's full Agent E2E remains blocked by its provider quota. Native Windows/Linux and Intel Mac real inference remain unverified. These limits do not change the successful CI and macOS backend results above.
