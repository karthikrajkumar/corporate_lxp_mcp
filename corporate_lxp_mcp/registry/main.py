"""Registry server entry point"""

import uvicorn

from .server import RegistryServer
from ..config.settings import get_settings


def main():
    """Main entry point for registry server"""
    settings = get_settings()
    registry = RegistryServer()
    
    uvicorn.run(
        registry.app,
        host=settings.registry_host,
        port=settings.registry_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
