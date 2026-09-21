from __future__ import annotations

from .router import core, decide


def main() -> int:
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("laya-router")

    @server.tool()
    def laya_decide(task: str) -> dict:
        """Return advisory local task decisions; unavailable results are fail open."""
        return decide(task)

    @server.tool()
    def laya_health() -> dict:
        """Return lightweight runtime health without downloading a model."""
        return core().info()

    @server.tool()
    def laya_info() -> dict:
        """Return backend and platform information."""
        return core().info()

    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
