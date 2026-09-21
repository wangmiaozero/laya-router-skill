#!/usr/bin/env python3
"""Compatibility entry point for existing helper and MCP invocations."""
from __future__ import annotations

import sys

from laya_router.cli import main as cli_main
from laya_router.mcp import main as mcp_main

if __name__ == "__main__":
    raise SystemExit(mcp_main() if "--mcp" in sys.argv else cli_main(["decide", *sys.argv[1:]]))
