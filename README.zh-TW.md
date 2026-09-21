# Laya Router Skill

[English](README.md) · [简体中文](README.zh-CN.md)

面向 AI Coding Agent 的跨平台本機決策路由 Skill，由 Laya / Laya-MLX 驅動。

支援 ChatGPT 桌面版（Codex）、Codex CLI、Claude Code、OpenCode、Pi 及相容 Agent Skills 的 Agent。是否自動呼叫取決於 Agent 的 Skill／工具選擇策略；明確呼叫請使用 CLI。

## 相容性

| 平台 | 後端 | 裝置 | 狀態 |
| --- | --- | --- | --- |
| Apple Silicon Mac | laya-mlx | MLX GPU | 已實作，待真實模型驗證 |
| Intel Mac | laya | CPU／可用的 MPS | 已實作，待真實模型驗證 |
| Windows | laya | CPU／CUDA | 已實作，已設定 CI |
| Linux | laya | CPU／CUDA | 已實作，已設定 CI |

| Agent | Skill | CLI | MCP |
| --- | --- | --- | --- |
| ChatGPT 桌面版（Codex） | 共用 Agent Skills 路徑 | 有 shell 工具時可用 | 透過公開 Codex CLI 盡力註冊 |
| Codex CLI | 共用路徑 | 支援 | 盡力註冊 |
| Claude Code | 個人 Skill 路徑 | 支援 | 需手動設定 |
| OpenCode | 相容共用路徑 | 支援 | 需手動設定 |
| Pi | 共用路徑 | 支援 | 需手動設定 |

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

CLI 位於獨立 venv 的 `bin`（Windows 為 `Scripts`）目錄，可用完整路徑呼叫或自行加入 PATH。兩種後端回傳統一 JSON。失敗時回傳 `status=unavailable`、`advisory=true`、`fail_open=true`，Agent 應繼續正常工作。

Laya 適合分類、路由、選擇、評分、`noul` 機率與風險提示；無法取代程式碼生成、除錯、架構推理、安全稽核或最終核准。基礎 checkpoint 在部分零樣本 typed-decision 情境下準確率有限。模型輸出絕不可直接當成命令執行。首次下載後推理在本機完成，預設不持久化任務全文。

解除安裝前可執行 `python3 scripts/uninstall.py --all --dry-run`，確認後執行 `python3 scripts/uninstall.py --all`。解除安裝器只刪除 manifest 記錄的本專案檔案與 MCP 項目，不刪除 Agent 設定目錄或全域模型快取。

詳見 [英文 README](README.md)、[架構](references/ARCHITECTURE.md)、[後端](references/BACKENDS.md) 與 [Agent 整合](references/AGENTS.md)。作者：wangmiao · tuziling84@gmail.com。授權 Apache-2.0。
