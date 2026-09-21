# laya-router-skill

[English](README.md) | 简体中文 | [繁體中文](README.zh-TW.md)

面向 Apple Silicon 的本地 Laya-MLX 决策路由，用于 Codex 和 Pi。

`laya-router-skill` 将可复用的 **Agent Skill** 与小型本地 MCP runtime 打包在一起。它基于 [laya-mlx](https://github.com/mizorewww/laya-mlx)，用于快速给出结构化决策，例如任务分类、复杂度评分、升级提示、工具使用提示，以及轻量级执行风险信号。

它**不能**替代 GPT、Codex、Pi、代码审查或安全判断。

## 为什么需要它

编码 Agent 经常把前沿模型的推理能力浪费在很小的路由问题上：

- 这个任务是琐碎还是复杂？
- 是否需要更强的推理？
- 这主要是前端、后端、架构还是安全工作？
- 是否很可能需要工具？
- 请求的操作是否异常危险？

Laya 可以在 Apple Silicon 上本地回答这类有约束的结构化问题。本项目把该能力做成 Agent 可复用的包。

## 环境要求

- Apple Silicon Mac（`arm64`）
- macOS 14+
- Python 3.11+
- Codex 和/或 Pi

## 安装

```bash
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
./scripts/install.sh
```

安装脚本会：

1. 创建 `~/.local/share/laya-router/.venv`
2. 安装 `laya-mlx` 和 MCP Python SDK
3. 将 skill 安装到 `~/.agents/skills/laya-router`
4. 尽力注册名为 `laya` 的 Codex MCP server

不会安装任何全局 Python 包。

## 用 Codex 安装

把下面这段话复制给 Codex 即可：

```text
在这台 Apple Silicon Mac 上安装并配置 https://github.com/wangmiaozero/laya-router-skill

请按顺序完成：
1. 确认系统是 macOS arm64，且 Python 为 3.11+。不满足就停止并说明原因。
2. 如果当前目录还没有这个仓库，先克隆再进入：
   git clone https://github.com/wangmiaozero/laya-router-skill.git
   cd laya-router-skill
3. 执行 ./scripts/install.sh
4. 执行 ./scripts/healthcheck.sh
5. 如果 Codex MCP 没有注册成功，执行：
   codex mcp add laya -- "$HOME/.local/share/laya-router/.venv/bin/python" "$HOME/.local/share/laya-router/server.py" --mcp
6. 用 codex mcp list 确认已有名为 laya 的 MCP server
7. 汇报 skill 路径、runtime 路径、healthcheck 结果、MCP 状态。

不要安装全局 Python 包。如果 Laya、MLX、模型或 MCP 不可用，按 fail-open 处理并报告错误，不要阻断后续工作。安装完成后，用本地 laya MCP 的 laya_decide 工具做任务分流；也可用 ./scripts/decide.sh。
```

## 日常使用

正常使用 Codex：

```bash
codex
```

或正常使用 Pi：

```bash
pi
```

Skill 可通过共享的 Agent Skills 路径被发现。Codex 也可以调用已注册的本地 `laya` MCP server。

## 显式调用

直接做本地决策：

```bash
./scripts/decide.sh "Refactor this Vue module to React and inspect risky changes"
```

在启用 skill 命令时，Pi 可以用 `/skill:laya-router` 显式加载该 skill。

## 健康检查

```bash
./scripts/healthcheck.sh
```

## 配置

运行时配置位于：

```text
~/.local/share/laya-router/config.json
```

默认模型：

```text
aac6fef/laya-multilingual-mlx
```

## 失败开放

如果 Laya、MLX、模型或 MCP 不可用，路由器会返回 unavailable / fail-open 结果。编码 Agent 应照常继续工作。

## 卸载

```bash
./scripts/uninstall.sh
```

这会移除 runtime 和已安装的 skill 符号链接，但不会删除你的仓库检出目录，也不会卸载 Codex 本身。

## 项目结构

```text
laya-router-skill/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── README.zh-TW.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── icon.svg
├── runtime/
│   └── server.py
├── scripts/
│   ├── install.sh
│   ├── decide.sh
│   ├── healthcheck.sh
│   └── uninstall.sh
├── references/
│   └── ARCHITECTURE.md
└── .github/
    └── workflows/
        └── shellcheck.yml
```

## 安全

Agent Skills 和 MCP server 会以当前用户权限执行代码。安装前请审查源码。不要把路由器当作破坏性操作或安全敏感操作的唯一审批门。

## 上游

- Laya：`convaiinnovations/laya`
- MLX 移植：`mizorewww/laya-mlx`

本项目是独立集成，与 Convai Innovations、OpenAI 或 laya-mlx 维护者没有从属关系。

## 作者

- wangmiao — tuziling84@gmail.com
- GitHub: https://github.com/wangmiaozero

## 许可证

Apache-2.0.
