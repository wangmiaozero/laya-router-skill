"""Opt-in real model and MCP checks: pytest -m integration."""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys

import pytest


@pytest.mark.integration
def test_real_cli_backend_and_utf8():
    for task in ("Fix a typo in README", "帮我检查这个大型项目的风险"):
        command = [sys.executable, "-m", "laya_router", "decide", task, "--json"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "ok"
        assert data["advisory"] is True
        assert data["backend"] in {"mlx", "torch"}
        assert all(data["answers"].values())


@pytest.mark.integration
def test_real_stdio_mcp():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def run():
        params = StdioServerParameters(command=sys.executable, args=["-m", "laya_router.mcp"], env=dict(os.environ))
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
                assert {"laya_health", "laya_info", "laya_decide"} <= {tool.name for tool in listed.tools}
                for name, arguments in (("laya_health", {}), ("laya_info", {}),
                                        ("laya_decide", {"task": "Refactor a large backend service and inspect risky changes"})):
                    result = await session.call_tool(name, arguments=arguments)
                    assert not result.isError
                    data = getattr(result, "structuredContent", None)
                    if data is None:
                        data = json.loads(result.content[0].text)
                    assert data["status"] in {"ok", "ready"}
                    if name == "laya_decide":
                        assert data["advisory"] is True
                        assert data["answers"]

    asyncio.run(run())
