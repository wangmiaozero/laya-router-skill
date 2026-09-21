# Security Policy

## Reporting

Please report security issues privately:

- GitHub Security Advisories: https://github.com/wangmiaozero/laya-router-skill/security/advisories/new
- Email: tuziling84@gmail.com

Do not open a public issue with exploit details.

## Threat model

This project installs executable Python code and can expose it to coding agents through MCP. It runs with the current user's permissions.

The Laya output is advisory only. Never use it as the sole authorization mechanism for destructive commands, credentials, production changes, or security-sensitive actions.

## Logging

The default runtime does not intentionally persist task text. Operational errors are written under `~/.local/share/laya-router/logs/`.
