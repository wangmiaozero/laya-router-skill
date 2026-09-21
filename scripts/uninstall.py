#!/usr/bin/env python3
"""Remove only paths recorded as owned by this project."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from install import data_dir


def plan_uninstall(base: Path, agents: list[str] | None = None, runtime: bool = False, all_items: bool = False) -> dict:
    manifest_path = base / "install-manifest.json"
    if not manifest_path.exists():
        return {"skills": [], "mcp": [], "paths": [], "manifest": False}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("owner") != "laya-router-skill":
        raise RuntimeError("Refusing unowned install manifest")
    selected = set(agents or [])
    skills = [(Path(path), details) for path, details in manifest.get("skills", {}).items()
              if all_items or runtime or bool(selected.intersection(details.get("agents", [details.get("agent")])))]
    mcp = [(name, details) for name, details in manifest.get("mcp", {}).items() if all_items or runtime or details.get("agent") in selected]
    paths = [Path(path) for path in manifest.get("paths", [])] if runtime or all_items else []
    return {"skills": skills, "mcp": mcp, "paths": paths, "manifest": True, "data": manifest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", default="")
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not (args.agents or args.runtime or args.all):
        parser.error("Specify --agents, --runtime, or --all")
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    if any(a not in {"codex", "claude", "opencode", "pi"} for a in agents):
        parser.error("Unknown agent")
    base = data_dir()
    try:
        plan = plan_uninstall(base, agents, args.runtime, args.all)
        summary = {"skills": [str(p) for p, _ in plan["skills"]], "mcp": [name for name, _ in plan["mcp"]], "paths": [str(p) for p in plan["paths"]]}
        if args.dry_run:
            print(json.dumps(summary, indent=2))
            return 0
        if not plan["manifest"]:
            print("No owned installation found")
            return 0
        manifest = plan["data"]
        for target, details in plan["skills"]:
            owners = set(details.get("agents", [details.get("agent")]))
            remaining = owners - set(agents)
            if remaining and not (args.all or args.runtime):
                details["agents"] = sorted(remaining)
                continue
            if details.get("mode") == "symlink" and target.is_symlink() and str(target.resolve()) == details.get("source"):
                target.unlink()
            elif details.get("mode") == "copy" and target.is_dir() and (target / "SKILL.md").exists():
                shutil.rmtree(target)
            else:
                print(f"Skipped changed skill: {target}")
                continue
            manifest["skills"].pop(str(target), None)
            backup = manifest.get("backups", {}).pop(str(target), None)
            if backup and Path(backup).exists() and not target.exists():
                Path(backup).rename(target)
        for name, details in plan["mcp"]:
            if details.get("agent") == "codex" and shutil.which("codex"):
                current = subprocess.run(["codex", "mcp", "get", name], capture_output=True, text=True)
                if current.returncode == 0 and details.get("command", "") in current.stdout:
                    subprocess.run(["codex", "mcp", "remove", name], check=False, capture_output=True)
                    manifest["mcp"].pop(name, None)
        for path in sorted(plan["paths"], key=lambda p: len(p.parts), reverse=True):
            if str(path) not in manifest["paths"] or path.parent != base or path.name not in {".venv", "skill", "config.json"}:
                continue
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            elif path.exists() or path.is_symlink():
                path.unlink()
            manifest["paths"].remove(str(path))
            backup = manifest.get("backups", {}).pop(str(path), None)
            if backup and Path(backup).exists():
                Path(backup).rename(path)
        manifest_path = base / "install-manifest.json"
        if not manifest["skills"] and not manifest["mcp"] and not manifest["paths"]:
            manifest_path.unlink()
            try:
                base.rmdir()
            except OSError:
                pass
        else:
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "complete", **summary}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Uninstall failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
