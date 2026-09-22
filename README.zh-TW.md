# Laya Router Skill

[English](README.md) · [简体中文](README.zh-CN.md)

面向 AI Coding Agent 的跨平台本機決策路由 Skill，由 Laya / Laya-MLX 驅動。

支援 ChatGPT Desktop (Codex)、Codex CLI、Claude Code、OpenCode、Pi 及相容 Agent Skills 的 Agent。是否自動呼叫取決於 Agent 的 Skill／工具選擇策略；明確呼叫請使用 CLI。

**發佈狀態：v0.2.0-rc.1。** 核心執行時期已在 Apple Silicon Mac 完成真實 MLX、PyTorch 與 stdio MCP 驗證；其他平台的真實推理和部分 Agent 端到端呼叫仍待驗證。

## 相容性

| 平台 | 後端 | CI | 真實推理 |
| --- | --- | --- | --- |
| Apple Silicon Mac | laya-mlx GPU；laya CPU/MPS | Python 3.11/3.12 已驗證 | macOS arm64 兩種後端已驗證 |
| Intel Mac | laya CPU/MPS | 待驗證 | E2E 待驗證 |
| Windows | laya CPU/CUDA | Python 3.11/3.12 已驗證 | E2E 待驗證 |
| Linux | laya CPU/CUDA | Python 3.11/3.12 已驗證 | E2E 待驗證 |

| 客戶端 | Skill 發現 | 明確呼叫 | 自動呼叫 | MCP | 狀態 |
| --- | --- | --- | --- | --- | --- |
| ChatGPT Desktop (Codex) | 本次對話已驗證 | CLI 助手已驗證 | E2E 待驗證 | 已註冊；UI E2E 待驗證 | 已實作／手動 UI E2E 待驗證 |
| Codex CLI | 已驗證 | `laya_decide` 與 MLX 已驗證 | 已選擇 Skill；真實推理未驗證 | 自動核准模式已驗證 | 明確 E2E 已驗證 |
| Claude Code | 已驗證 | Skill → CLI → MLX 已驗證 | 已選擇 Skill；真實推理未驗證 | 未設定 | 明確 E2E 已驗證 |
| OpenCode | 已驗證 | Skill → CLI → MLX 已驗證 | 已選擇 Skill；真實推理未驗證 | 未設定 | 明確 E2E 已驗證 |
| Pi | 已驗證 | 提供者額度限制，E2E 待驗證 | E2E 待驗證 | 未設定 | E2E 待驗證 |

ChatGPT Desktop (Codex) 手動驗收：重新啟動應用程式，開啟 Codex，確認可找到 Laya Router Skill，送出適合分類的程式任務，檢查 Skill／MCP 沒有錯誤，並記錄是否實際呼叫。自動呼叫不保證發生。既有名為 `laya` 的 MCP 項目不會被覆蓋；新項目名為 `laya-router`。

Agent E2E 的證據和限制見 [AGENT_E2E.md](references/AGENT_E2E.md)。每次決策僅向使用者資料目錄的 `logs/events.jsonl` 附加時間、來源、工具、後端、執行時期、狀態、耗時和任務 SHA-256 雜湊；不記錄完整任務文字。

[RC 跨平台 CI](https://github.com/wangmiaozero/laya-router-skill/actions/runs/35574162049) 的 Ubuntu、Windows、macOS × Python 3.11/3.12 共六個作業全部通過。一般 CI 不執行真實模型推理。

## 安裝

建議使用 Python 3.11 或 3.12。安裝器建立獨立 venv，不在全域安裝 Python 套件。模型在首次決策時才下載。

macOS／Linux：

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

`--agents auto` 只選偵測到的 Agent；`--agents all` 安裝全部 Skill；`--agents codex,claude,opencode,pi` 指定 Agent。亦可使用 `--backend auto|mlx|torch`、`--no-mcp`、`--dry-run`、`--force` 與 `--yes`。預設跳過非本專案擁有的既有 Skill。

`--backend` 決定安裝的後端依賴，並寫入新建設定；重複安裝會保留既有 `config.json`。若要變更執行時期後端，請修改設定中的 `backend` 欄位。

## 使用

```sh
laya-router decide "重構這個模組並評估風險" --json
laya-router health
laya-router info
laya-router config
laya-router backend
laya-router version
python3 scripts/healthcheck.py --json
```

安裝器會在 macOS/Linux 已有的 `~/.local/bin` 建立使用者級 launcher；Windows 使用使用者資料目錄的 `bin`。它會顯示 `PATH status: READY` 或 `ACTION REQUIRED`，不會修改 shell 設定或系統環境變數。如需自行加入 PATH，可執行 `export PATH="$HOME/.local/bin:$PATH"`。亦可使用獨立 venv 的 CLI 完整路徑呼叫。每次 CLI 呼叫都是獨立行程，會重新載入模型；可選的 MCP 長期行程可保持模型常駐。兩種後端回傳統一 JSON。失敗時回傳 `status=unavailable`、`advisory=true`、`fail_open=true`，Agent 應繼續正常工作。

Laya 適合分類、路由、選擇、評分、`noul` 機率與風險提示；無法取代程式碼生成、除錯、架構推理、安全稽核或最終核准。基礎 checkpoint 在部分零樣本 typed-decision 情境下準確率有限；路由信心值不等於真實正確率。模型輸出絕不可直接當成命令執行。首次下載後推理在本機完成，預設不持久化任務全文。

解除安裝前可執行 `python3 scripts/uninstall.py --all --dry-run`，確認後執行 `python3 scripts/uninstall.py --all`。解除安裝器只刪除 manifest 記錄的本專案檔案與 MCP 項目，不刪除 Agent 設定目錄或全域模型快取。

真實模型與 MCP 測試標記為 `integration`，一般 `pytest` 預設跳過。使用隔離 venv 安裝相應後端和 MCP SDK 後，執行 `python -m pytest -m integration`；此命令可能下載 checkpoint。一般 PR CI 不下載大型模型，手動 workflow dispatch 可明確啟用。

詳見 [英文 README](README.md)、[架構](references/ARCHITECTURE.md)、[後端](references/BACKENDS.md) 與 [Agent 整合](references/AGENTS.md)。作者：wangmiao · tuziling84@gmail.com。授權 Apache-2.0。
