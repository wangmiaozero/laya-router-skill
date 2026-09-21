# Laya Router Skill

[English](README.md) · [繁體中文](README.zh-TW.md)

面向 AI Coding Agent 的跨平台本地决策路由 Skill，由 Laya / Laya-MLX 驱动。

支持 ChatGPT 桌面版（Codex）、Codex CLI、Claude Code、OpenCode、Pi 与兼容 Agent Skills 的 Agent。是否自动调用取决于 Agent 的 Skill/工具选择策略；显式调用请使用 CLI。

## 兼容性

| 平台 | 后端 | 设备 | 状态 |
| --- | --- | --- | --- |
| Apple Silicon Mac | laya-mlx | MLX GPU | 已实现，待真实模型验证 |
| Intel Mac | laya | CPU / 可用的 MPS | 已实现，待真实模型验证 |
| Windows | laya | CPU / CUDA | 已实现，已配置 CI |
| Linux | laya | CPU / CUDA | 已实现，已配置 CI |

| Agent | Skill | CLI | MCP |
| --- | --- | --- | --- |
| ChatGPT 桌面版（Codex） | 共享 Agent Skills 路径 | 有 shell 工具时可用 | 通过公开 Codex CLI 尽力注册 |
| Codex CLI | 共享路径 | 支持 | 尽力注册 |
| Claude Code | 个人 Skill 路径 | 支持 | 需手动配置 |
| OpenCode | 兼容共享路径 | 支持 | 需手动配置 |
| Pi | 共享路径 | 支持 | 需手动配置 |

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

CLI 位于独立 venv 的 `bin`（Windows 为 `Scripts`）目录，可用完整路径调用或自行加入 PATH。六类结果是任务类型、复杂度、强推理需求、工具需求、安全敏感性与风险。两种后端返回统一 JSON。失败时返回 `status=unavailable`、`advisory=true`、`fail_open=true`，Agent 应继续正常工作。

Laya 适合分类、路由、选择、评分、`noul` 概率与风险提示；不能替代代码生成、调试、架构推理、安全审计或最终批准。基础 checkpoint 在部分零样本 typed-decision 场景中准确率有限。模型输出绝不能直接执行为命令。首次下载后推理在本地完成，默认不持久化任务全文。

卸载前可运行 `python3 scripts/uninstall.py --all --dry-run`，确认后运行 `python3 scripts/uninstall.py --all`。卸载器只删除 manifest 记录的本项目文件和 MCP 条目，不删除 Agent 配置目录或全局模型缓存。

详细说明见 [英文 README](README.md)、[架构](references/ARCHITECTURE.md)、[后端](references/BACKENDS.md) 与 [Agent 集成](references/AGENTS.md)。作者：wangmiao · tuziling84@gmail.com。许可证 Apache-2.0。
