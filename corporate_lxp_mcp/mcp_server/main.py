"""MCP server entry point for Corporate LXP platform."""

import asyncio
import logging
import os

from .server import CorporateLXPServer


def main() -> None:
    """Launch the production-ready MCP server."""
    log_level = os.getenv("CORPORATE_LXP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)

    server = CorporateLXPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
