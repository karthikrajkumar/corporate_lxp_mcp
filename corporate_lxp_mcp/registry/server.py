"""MCP Registry Server for service discovery following SOLID principles"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from ..config.settings import get_settings


class MCPServerInfo(BaseModel):
    """MCP Server information model"""
    id: str = Field(..., description="Unique server identifier")
    name: str = Field(..., description="Server name")
    description: str = Field(..., description="Server description")
    version: str = Field(..., description="Server version")
    host: str = Field(..., description="Server host address")
    port: int = Field(..., gt=0, le=65535, description="Server port")
    protocol: str = Field(default="stdio", description="Communication protocol")
    capabilities: List[str] = Field(default_factory=list, description="Server capabilities")
    tools: List[str] = Field(default_factory=list, description="Available tools")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    registered_at: datetime = Field(default_factory=datetime.now, description="Registration timestamp")
    last_heartbeat: datetime = Field(default_factory=datetime.now, description="Last heartbeat timestamp")
    status: str = Field(default="active", description="Server status")


class RegistrationRequest(BaseModel):
    """MCP Server registration request"""
    name: str = Field(..., description="Server name")
    description: str = Field(..., description="Server description")
    version: str = Field(..., description="Server version")
    host: str = Field(..., description="Server host address")
    port: int = Field(..., gt=0, le=65535, description="Server port")
    protocol: str = Field(default="stdio", description="Communication protocol")
    capabilities: List[str] = Field(default_factory=list, description="Server capabilities")
    tools: List[str] = Field(default_factory=list, description="Available tools")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class RegistryServer:
    """MCP Registry Server for service discovery"""

    def __init__(self):
        """Initialize registry server"""
        self.app = FastAPI(
            title="MCP Registry",
            description="Registry service for MCP server discovery",
            version="1.0.0"
        )
        self.settings = get_settings()
        self.servers: Dict[str, MCPServerInfo] = {}
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.post("/register", response_model=MCPServerInfo, status_code=status.HTTP_201_CREATED)
        async def register_server(request: RegistrationRequest):
            """Register a new MCP server"""
            server_info = MCPServerInfo(
                id=str(uuid4()),
                **request.dict()
            )
            
            self.servers[server_info.id] = server_info
            return server_info

        @self.app.get("/servers", response_model=List[MCPServerInfo])
        async def list_servers():
            """List all registered MCP servers"""
            self._cleanup_stale_servers()
            return list(self.servers.values())

        @self.app.get("/servers/{server_id}", response_model=MCPServerInfo)
        async def get_server(server_id: str):
            """Get specific server information"""
            if server_id not in self.servers:
                raise HTTPException(status_code=404, detail="Server not found")
            
            server = self.servers[server_id]
            if self._is_server_stale(server):
                raise HTTPException(status_code=404, detail="Server not available")
            
            return server

        @self.app.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def unregister_server(server_id: str):
            """Unregister a server"""
            if server_id not in self.servers:
                raise HTTPException(status_code=404, detail="Server not found")
            
            del self.servers[server_id]

        @self.app.post("/servers/{server_id}/heartbeat")
        async def heartbeat(server_id: str):
            """Update server heartbeat"""
            if server_id not in self.servers:
                raise HTTPException(status_code=404, detail="Server not found")
            
            self.servers[server_id].last_heartbeat = datetime.now()
            self.servers[server_id].status = "active"
            
            return {"message": "Heartbeat received"}

        @self.app.get("/mcp-config")
        async def generate_mcp_config():
            """Generate MCP configuration file"""
            self._cleanup_stale_servers()

            config = {"mcpServers": {}}
            client_registry_host = (
                "localhost"
                if self.settings.registry_host in {"0.0.0.0", "127.0.0.1"}
                else self.settings.registry_host
            )
            for server in self.servers.values():
                if server.status == "active":
                    config["mcpServers"][server.name.replace("-", "_")] = {
                        "command": "python",
                        "args": ["-m", "corporate_lxp_mcp.mcp_server.main"],
                        "env": {
                            "CORPORATE_LXP_REGISTRY_HOST": client_registry_host,
                            "CORPORATE_LXP_REGISTRY_PORT": str(self.settings.registry_port),
                            "CORPORATE_LXP_LOG_LEVEL": self.settings.log_level,
                            "SERVER_ID": server.id,
                            "PYTHONPATH": ".",
                        }
                    }

            return config

        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {"service": "MCP Registry", "version": "1.0.0"}

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "mcp-registry",
                "active_servers": len([s for s in self.servers.values() if s.status == "active"])
            }

    def _cleanup_stale_servers(self):
        """Remove stale servers (no heartbeat for 5 minutes)"""
        stale_threshold = datetime.now() - timedelta(minutes=5)
        stale_servers = [
            server_id for server_id, server in self.servers.items()
            if server.last_heartbeat < stale_threshold
        ]
        
        for server_id in stale_servers:
            self.servers[server_id].status = "inactive"

    def _is_server_stale(self, server: MCPServerInfo) -> bool:
        """Check if server is stale"""
        stale_threshold = datetime.now() - timedelta(minutes=5)
        return server.last_heartbeat < stale_threshold
