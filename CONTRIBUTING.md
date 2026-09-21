# Contributing

Issues and pull requests are welcome:

https://github.com/wangmiaozero/laya-router-skill/issues

Maintainer: wangmiao <tuziling84@gmail.com>

## Principles

- keep the skill compatible with the Agent Skills directory layout
- avoid replacing or wrapping the official `codex` binary
- keep runtime dependencies isolated
- preserve fail-open behavior
- do not turn Laya into an authorization authority
- document behavioral changes

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install laya-mlx mcp
python runtime/server.py "Implement a small README fix"
```
