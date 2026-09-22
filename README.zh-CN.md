# Laya Router Skill

[English](README.md) · [繁體中文](README.zh-TW.md)

面向 AI Coding Agent 的跨平台本地决策路由 Skill，由 Laya / Laya-MLX 驱动。

支持 ChatGPT Desktop (Codex)、Codex CLI、Claude Code、OpenCode、Pi 与兼容 Agent Skills 的 Agent。是否自动调用取决于 Agent 的 Skill/工具选择策略；显式调用请使用 CLI。

**发布状态：v0.2.0-rc.1。** 核心运行时已在 Apple Silicon Mac 上完成真实 MLX、PyTorch 和 stdio MCP 验证；其他平台的真实推理及部分 Agent 端到端调用仍待验证。

## 兼容性

| 平台 | 后端 | CI | 真实推理 |
| --- | --- | --- | --- |
| Apple Silicon Mac | laya-mlx GPU；laya CPU/MPS | Python 3.11/3.12 已验证 | macOS arm64 两种后端已验证 |
| Intel Mac | laya CPU/MPS | 待验证 | E2E 待验证 |
| Windows | laya CPU/CUDA | Python 3.11/3.12 已验证 | E2E 待验证 |
| Linux | laya CPU/CUDA | Python 3.11/3.12 已验证 | E2E 待验证 |

| 客户端 | Skill 发现 | 显式调用 | 隐式调用 | MCP | 状态 |
| --- | --- | --- | --- | --- | --- |
| ChatGPT Desktop (Codex) | 本会话已验证 | CLI 助手已验证 | E2E 待验证 | 已注册；UI E2E 待验证 | 已实现／手动 UI E2E 待验证 |
| Codex CLI | 已验证 | `laya_decide` 与 MLX 已验证 | 已选择 Skill；真实推理未验证 | 自动审批模式已验证 | 显式 E2E 已验证 |
| Claude Code | 已验证 | Skill → CLI → MLX 已验证 | 已选择 Skill；真实推理未验证 | 未配置 | 显式 E2E 已验证 |
| OpenCode | 已验证 | Skill → CLI → MLX 已验证 | 已选择 Skill；真实推理未验证 | 未配置 | 显式 E2E 已验证 |
| Pi | 已验证 | 提供方额度限制，E2E 待验证 | E2E 待验证 | 未配置 | E2E 待验证 |

ChatGPT Desktop (Codex) 手动验收：重启应用，打开 Codex，确认可发现 Laya Router Skill，提交适合分类的编码任务，检查 Skill／MCP 没有报错，并记录是否实际调用。自动调用不保证发生。已有名为 `laya` 的 MCP 条目不会被覆盖；新条目名为 `laya-router`。

Agent E2E 的证据和限制见 [AGENT_E2E.md](references/AGENT_E2E.md)。每次决策仅向用户数据目录的 `logs/events.jsonl` 追加时间、来源、工具、后端、运行时、状态、耗时和任务 SHA-256 哈希；不记录完整任务文本。

[RC 跨平台 CI](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35574162049) 的 Ubuntu、Windows、macOS × Python 3.11/3.12 共六个作业全部通过。普通 CI 不做真实模型推理。

## 安装

推荐 Python 3.11 或 3.12。安装器创建独立 venv，不全局安装 Python 包。模型在首次决策时才下载。

macOS / Linux：

```sh
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
python3 scripts/install.py
```

Windows PowerShell：

```powershell
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
py -3 scripts\install.py
```

`--agents auto` 只选检测到的 Agent；`--agents all` 安装全部 Skill；`--agents codex,claude,opencode,pi` 指定 Agent。`--backend auto|mlx|torch`、`--no-mcp`、`--dry-run`、`--force` 和 `--yes` 可用于控制安装。默认跳过非本项目拥有的既有 Skill。

`--backend` 决定安装的后端依赖，并写入新建配置；重复安装会保留既有 `config.json`。要改变运行时后端，请修改配置中的 `backend` 字段。

## 使用

```sh
laya-router decide "重构这个模块并评估风险" --json
laya-router health
laya-router info
laya-router config
laya-router backend
laya-router version
python3 scripts/healthcheck.py --json
```

安装器会在 macOS/Linux 已有的 `~/.local/bin` 中创建用户级 launcher；Windows 则使用用户数据目录的 `bin`。它会显示 `PATH status: READY` 或 `ACTION REQUIRED`，不会修改 shell 配置或系统环境变量。如需自行加入 PATH，可执行 `export PATH="$HOME/.local/bin:$PATH"`。也可以用独立 venv 中的 CLI 完整路径调用。每次 CLI 调用都是独立进程，会重新加载模型；可选 MCP 长进程可保持模型常驻。六类结果是任务类型、复杂度、强推理需求、工具需求、安全敏感性与风险。两种后端返回统一 JSON。失败时返回 `status=unavailable`、`advisory=true`、`fail_open=true`，Agent 应继续正常工作。

Laya 适合分类、路由、选择、评分、`noul` 概率与风险提示；不能替代代码生成、调试、架构推理、安全审计或最终批准。基础 checkpoint 在部分零样本 typed-decision 场景中准确率有限；路由置信度不等于真实正确率。模型输出绝不能直接执行为命令。首次下载后推理在本地完成，默认不持久化任务全文。

卸载前可运行 `python3 scripts/uninstall.py --all --dry-run`，确认后运行 `python3 scripts/uninstall.py --all`。卸载器只删除 manifest 记录的本项目文件和 MCP 条目，不删除 Agent 配置目录或全局模型缓存。

真实模型和 MCP 测试标记为 `integration`，普通 `pytest` 默认跳过。使用隔离 venv 安装相应后端及 MCP SDK 后，运行 `python -m pytest -m integration`；该命令可能下载 checkpoint。普通 PR CI 不下载大模型，手动 workflow dispatch 可显式启用。

详细说明见 [英文 README](README.md)、[架构](references/ARCHITECTURE.md)、[后端](references/BACKENDS.md) 与 [Agent 集成](references/AGENTS.md)。作者：wangmiao · tuziling84@gmail.com。许可证 Apache-2.0。
