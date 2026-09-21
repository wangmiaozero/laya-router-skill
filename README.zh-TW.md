# laya-router-skill

[English](README.md) | [简体中文](README.zh-CN.md) | 繁體中文

面向 Apple Silicon 的本機 Laya-MLX 決策路由，用於 Codex 與 Pi。

`laya-router-skill` 將可重複使用的 **Agent Skill** 與小型本機 MCP runtime 打包在一起。它基於 [laya-mlx](https://github.com/mizorewww/laya-mlx)，用於快速給出結構化決策，例如任務分類、複雜度評分、升級提示、工具使用提示，以及輕量級執行風險訊號。

它**不能**取代 GPT、Codex、Pi、程式碼審查或安全判斷。

## 為什麼需要它

編碼 Agent 經常把前沿模型的推理能力浪費在很小的路由問題上：

- 這個任務是瑣碎還是複雜？
- 是否需要更強的推理？
- 這主要是前端、後端、架構還是安全工作？
- 是否很可能需要工具？
- 請求的操作是否異常危險？

Laya 可以在 Apple Silicon 上本機回答這類有約束的結構化問題。本專案把該能力做成 Agent 可重複使用的套件。

## 環境需求

- Apple Silicon Mac（`arm64`）
- macOS 14+
- Python 3.11+
- Codex 和／或 Pi

## 安裝

```bash
git clone https://github.com/wangmiaozero/laya-router-skill.git
cd laya-router-skill
./scripts/install.sh
```

安裝腳本會：

1. 建立 `~/.local/share/laya-router/.venv`
2. 安裝 `laya-mlx` 與 MCP Python SDK
3. 將 skill 安裝到 `~/.agents/skills/laya-router`
4. 盡力註冊名為 `laya` 的 Codex MCP server

不會安裝任何全域 Python 套件。

## 用 Codex 安裝

把下面這段話複製給 Codex 即可：

```text
在這台 Apple Silicon Mac 上安裝並設定 https://github.com/wangmiaozero/laya-router-skill

請依序完成：
1. 確認系統是 macOS arm64，且 Python 為 3.11+。不滿足就停止並說明原因。
2. 如果目前目錄還沒有這個儲存庫，先複製再進入：
   git clone https://github.com/wangmiaozero/laya-router-skill.git
   cd laya-router-skill
3. 執行 ./scripts/install.sh
4. 執行 ./scripts/healthcheck.sh
5. 如果 Codex MCP 沒有註冊成功，執行：
   codex mcp add laya -- "$HOME/.local/share/laya-router/.venv/bin/python" "$HOME/.local/share/laya-router/server.py" --mcp
6. 用 codex mcp list 確認已有名為 laya 的 MCP server
7. 回報 skill 路徑、runtime 路徑、healthcheck 結果、MCP 狀態。

不要安裝全域 Python 套件。如果 Laya、MLX、模型或 MCP 無法使用，按 fail-open 處理並回報錯誤，不要阻斷後續工作。安裝完成後，用本機 laya MCP 的 laya_decide 工具做任務分流；也可用 ./scripts/decide.sh。
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

Skill 可透過共用的 Agent Skills 路徑被發現。Codex 也可以呼叫已註冊的本機 `laya` MCP server。

## 顯式呼叫

直接做本機決策：

```bash
./scripts/decide.sh "Refactor this Vue module to React and inspect risky changes"
```

在啟用 skill 命令時，Pi 可以用 `/skill:laya-router` 顯式載入該 skill。

## 健康檢查

```bash
./scripts/healthcheck.sh
```

## 設定

執行時期設定位於：

```text
~/.local/share/laya-router/config.json
```

預設模型：

```text
aac6fef/laya-multilingual-mlx
```

## 失敗開放

如果 Laya、MLX、模型或 MCP 無法使用，路由器會回傳 unavailable / fail-open 結果。編碼 Agent 應照常繼續工作。

## 解除安裝

```bash
./scripts/uninstall.sh
```

這會移除 runtime 與已安裝的 skill 符號連結，但不會刪除你的儲存庫檢出目錄，也不會解除安裝 Codex 本身。

## 專案結構

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

Agent Skills 與 MCP server 會以目前使用者權限執行程式碼。安裝前請審查原始碼。不要把路由器當作破壞性操作或安全敏感操作的唯一核准門檻。

## 上游

- Laya：`convaiinnovations/laya`
- MLX 移植：`mizorewww/laya-mlx`

本專案是獨立整合，與 Convai Innovations、OpenAI 或 laya-mlx 維護者沒有從屬關係。

## 作者

- wangmiao — tuziling84@gmail.com
- GitHub: https://github.com/wangmiaozero

## 授權條款

Apache-2.0.
