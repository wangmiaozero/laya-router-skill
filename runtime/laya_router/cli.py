from __future__ import annotations

import argparse
import json

from . import __version__
from .config import CONFIG_PATH, load_config
from .router import core, decide


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="laya-router")
    sub = parser.add_subparsers(dest="command", required=True)
    decision = sub.add_parser("decide")
    decision.add_argument("task")
    decision.add_argument("--json", action="store_true")
    for name in ("health", "info", "config", "backend", "version"):
        p = sub.add_parser(name)
        if name in {"health", "info", "config", "backend"}:
            p.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "decide":
        result = decide(args.task, source="cli")
    elif args.command == "config":
        result = {"path": str(CONFIG_PATH), "config": load_config()}
    elif args.command == "backend":
        result = core().info()
    elif args.command == "info":
        result = {"name": "Laya Router", "version": __version__, **core().info()}
    else:
        result = {"name": "Laya Router Health", "version": __version__, **core().info()}
    if getattr(args, "json", False) or args.command in {"decide", "config", "backend"}:
        print(json.dumps(result, ensure_ascii=False))
    else:
        for key, value in result.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    return 0
