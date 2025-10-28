"""Main entry point for Corporate LXP API server"""

import uvicorn

from .config.settings import get_settings
from .api.main import app


def main():
    """Main entry point"""
    settings = get_settings()
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
