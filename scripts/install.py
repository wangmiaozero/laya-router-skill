#!/usr/bin/env python3
"""Authoritative, cross-platform installer. Does not install packages globally."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
import venv

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ("codex", "claude", "opencode", "pi")


def data_dir() -> Path:
    """Bootstrap platformdirs' user_data_dir convention before the venv exists."""
    try:
        from platformdirs import user_data_dir
        return Path(user_data_dir("laya-router", "laya-router"))
    except ImportError:
        if sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "laya-router"
        if os.name == "nt":
            return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "laya-router" / "laya-router"
        return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "laya-router"


def skill_paths() -> dict[str, Path]:
    shared = Path.home() / ".agents" / "skills" / "laya-router"
    return {"codex": shared, "opencode": shared, "pi": shared,
            "claude": Path.home() / ".claude" / "skills" / "laya-router"}


def detected_agents() -> list[str]:
    return [agent for agent in AGENTS if shutil.which(agent)]


def choose_agents(value: str) -> list[str]:
    if value == "auto":
        return detected_agents()
    if value == "all":
        return list(AGENTS)
    result = [part.strip() for part in value.split(",") if part.strip()]
    if not result or any(part not in AGENTS for part in result):
        raise ValueError("--agents must be auto, all, or comma-separated codex,claude,opencode,pi")
    return list(dict.fromkeys(result))


def install_plan(agents: list[str], base: Path | None = None) -> dict:
    base = base or data_dir()
    paths = skill_paths()
    return {"data_dir": str(base), "venv": str(base / ".venv"), "skill_source": str(base / "skill"),
            "skill_paths": {agent: str(paths[agent]) for agent in agents}, "agents_detected": detected_agents()}


def python_in_venv(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def link_or_copy(source: Path, target: Path) -> str:
    try:
        target.symlink_to(source, target_is_directory=True)
        return "symlink"
    except OSError:
        shutil.copytree(source, target)
        return "copy"


def launcher_path(base: Path) -> Path | None:
    if os.name == "nt":
        return base / "bin" / "laya-router.cmd"
    user_bin = Path.home() / ".local" / "bin"
    return user_bin / "laya-router" if user_bin.is_dir() else None


def launcher_content(python: Path, windows: bool | None = None) -> str:
    if windows is None:
        windows = os.name == "nt"
    if windows:
        return f'@echo off\r\n"{python}" -m laya_router %*\r\n'
    return f'#!/bin/sh\nexec {shlex.quote(str(python))} -m laya_router "$@"\n'


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", default="auto")
    parser.add_argument("--backend", choices=("auto", "mlx", "torch"), default="auto")
    parser.add_argument("--no-mcp", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args(argv)
    try:
        agents = choose_agents(args.agents)
    except ValueError as exc:
        parser.error(str(exc))
    if sys.version_info < (3, 11):
        parser.error("Python 3.11+ required")
    machine = __import__("platform").machine().lower()
    apple = sys.platform == "darwin" and machine in {"arm64", "aarch64"}
    if args.backend == "mlx" and not apple:
        parser.error("MLX requires macOS Apple Silicon")
    base = data_dir()
    plan = install_plan(agents, base)
    plan.update({"backend": args.backend, "mcp": not args.no_mcp and "codex" in agents and bool(shutil.which("codex")),
                 "launcher": str(launcher_path(base)) if launcher_path(base) else None})
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    base.mkdir(parents=True, exist_ok=True)
    manifest_path = base / "install-manifest.json"
    manifest_valid = False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"owner": "laya-router-skill", "paths": [], "skills": {}, "mcp": {}}
        if manifest.get("owner") != "laya-router-skill":
            raise RuntimeError("Existing manifest is not owned by this project")
        manifest_valid = True
        manifest.setdefault("launchers", {})
        paths = set(manifest["paths"])
        venv_dir = base / ".venv"
        if not venv_dir.exists():
            venv.EnvBuilder(with_pip=True).create(venv_dir)
            paths.add(str(venv_dir))
        python = python_in_venv(venv_dir)
        package = "mlx" if (args.backend == "mlx" or args.backend == "auto" and apple) else "torch"
        optional = ",mcp" if plan["mcp"] else ""
        def pip_install(extra: str) -> None:
            subprocess.run([str(python), "-m", "pip", "install", f"{ROOT}[{extra}]"], check=True)
        try:
            pip_install(package + optional)
        except subprocess.CalledProcessError:
            if args.backend == "auto" and package == "mlx":
                print("MLX installation failed; trying PyTorch", file=sys.stderr)
                pip_install("torch" + optional)
            else:
                print("Backend installation failed; CLI remains fail open", file=sys.stderr)
                subprocess.run([str(python), "-m", "pip", "install", str(ROOT)], check=True)
        source = base / "skill"
        if source.exists():
            if str(source) not in paths and not args.force:
                raise RuntimeError(f"Unowned skill source: {source}; use --force after review")
            if str(source) in paths:
                shutil.rmtree(source)
            else:
                backup = source.with_name(source.name + f".backup-{int(time.time())}")
                source.rename(backup)
                manifest.setdefault("backups", {})[str(source)] = str(backup)
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "*.egg-info"))
        paths.add(str(source))
        config_path = base / "config.json"
        if not config_path.exists():
            config_path.write_text(json.dumps({"enabled": True, "backend": args.backend, "model": "auto", "language": "auto", "device": "auto", "fallback_on_error": True, "persist_task_text": False, "log_level": "INFO"}, indent=2) + "\n", encoding="utf-8")
            paths.add(str(config_path))
        launcher = launcher_path(base)
        launcher_installed = False
        if launcher:
            body = launcher_content(python).encode("utf-8")
            key = str(launcher)
            if launcher.exists():
                owned = manifest["launchers"].get(key)
                current = digest(launcher.read_bytes())
                if owned and current != owned["sha256"] and not args.force:
                    raise RuntimeError(f"Owned CLI launcher changed: {launcher}")
                if not owned and not args.force:
                    print(f"Skipping existing unowned CLI launcher: {launcher}", file=sys.stderr)
                else:
                    if current != digest(body) and not owned:
                        backup = launcher.with_name(launcher.name + f".backup-{int(time.time())}")
                        launcher.rename(backup)
                        manifest.setdefault("backups", {})[key] = str(backup)
                    launcher.write_bytes(body)
                    launcher_installed = True
            else:
                launcher.parent.mkdir(parents=True, exist_ok=True)
                launcher.write_bytes(body)
                launcher_installed = True
            if launcher_installed:
                if os.name != "nt":
                    launcher.chmod(0o755)
                manifest["launchers"][key] = {"sha256": digest(body), "python": str(python)}
        for agent, target in {a: skill_paths()[a] for a in agents}.items():
            key = str(target)
            if target.exists() or target.is_symlink():
                if key in manifest["skills"]:
                    old = manifest["skills"][key]
                    if old["mode"] == "symlink" and (not target.is_symlink() or target.resolve() != source.resolve()):
                        raise RuntimeError(f"Owned skill path changed: {target}")
                    if target.is_symlink():
                        target.unlink()
                    else:
                        shutil.rmtree(target)
                elif not args.force:
                    print(f"Skipping existing unowned skill: {target}", file=sys.stderr)
                    continue
                else:
                    backup = target.with_name(target.name + f".backup-{int(time.time())}")
                    target.rename(backup)
                    manifest.setdefault("backups", {})[key] = str(backup)
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = link_or_copy(source, target)
            owners = sorted(set(a for a in agents if skill_paths()[a] == target).union(manifest["skills"].get(key, {}).get("agents", [])))
            manifest["skills"][key] = {"mode": mode, "source": str(source), "agents": owners}
        if plan["mcp"]:
            name = "laya-router"
            existing = subprocess.run(["codex", "mcp", "get", name], capture_output=True, text=True)
            if existing.returncode != 0:
                command = ["codex", "mcp", "add", name, "--", str(python), "-m", "laya_router.mcp"]
                registered = subprocess.run(command, capture_output=True, text=True)
                if registered.returncode == 0:
                    manifest["mcp"][name] = {"agent": "codex", "command": str(python)}
                else:
                    print("Codex MCP registration unavailable; CLI and skill remain installed", file=sys.stderr)
            elif name not in manifest["mcp"]:
                print("Existing unowned Codex MCP entry left unchanged", file=sys.stderr)
        manifest["paths"] = sorted(paths)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if launcher_installed:
            print(f"CLI launcher installed: {launcher}")
        else:
            print(f"CLI launcher unavailable; use: {python} -m laya_router")
        on_path = launcher_installed and str(launcher.parent) in os.environ.get("PATH", "").split(os.pathsep)
        print(f"PATH status: {'READY' if on_path else 'ACTION REQUIRED'}")
        if not on_path and os.name != "nt":
            print('Add to your shell PATH manually: export PATH="$HOME/.local/bin:$PATH"')
        elif not on_path:
            print(f"Add {launcher.parent if launcher else base / 'bin'} to your user PATH manually")
        print(json.dumps({"status": "installed", **plan}, indent=2))
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        if manifest_valid:
            manifest["paths"] = sorted(paths)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Installation incomplete: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
