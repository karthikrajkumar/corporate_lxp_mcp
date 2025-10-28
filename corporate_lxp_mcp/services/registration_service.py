"""Registration service for MCP server following SOLID principles"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import aiohttp

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class RegistrationService:
    """Service for handling MCP server registration with registry"""

    def __init__(self):
        """Initialize registration service"""
        self.settings = get_settings()
        self.server_id: Optional[str] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        # In Docker, use the service name for inter-container communication
        if self.settings.registry_host == "0.0.0.0":
            registry_host = "registry"  # Docker service name
        else:
            registry_host = self.settings.registry_host
        self.registry_url = f"http://{registry_host}:{self.settings.registry_port}"
        self.is_registered = False

    async def register_server(self) -> bool:
        """Register MCP server with registry"""
        try:
            registration_data = {
                "name": self.settings.mcp_server_name,
                "description": "Corporate Learning Experience Platform MCP Server",
                "version": self.settings.mcp_server_version,
                "host": "localhost",
                "port": 9999,  # Dummy port for stdio MCP servers
                "protocol": "stdio",
                "capabilities": ["tools", "resources"],
                "tools": [
                    "list_employees", "get_employee", "create_employee", "update_employee",
                    "delete_employee", "get_employee_training", "get_employee_skills",
                    "get_department_employees", "update_training_progress",
                    "list_departments", "list_training_programs"
                ],
                "metadata": {
                    "platform": "corporate-lxp",
                    "version": self.settings.mcp_server_version,
                    "registered_at": datetime.now().isoformat()
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.registry_url}/register",
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        self.server_id = result["id"]
                        self.is_registered = True
                        logger.info(f"Successfully registered MCP server with ID: {self.server_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Registration failed: {response.status} - {error_text}")
                        return False

        except Exception as e:
            logger.error(f"Error registering MCP server: {e}")
            return False

    async def unregister_server(self) -> bool:
        """Unregister MCP server from registry"""
        if not self.server_id:
            return True

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(f"{self.registry_url}/servers/{self.server_id}") as response:
                    if response.status == 204:
                        logger.info("Successfully unregistered MCP server")
                        return True
                    else:
                        logger.error(f"Unregistration failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error unregistering MCP server: {e}")
            return False

    async def send_heartbeat(self) -> bool:
        """Send heartbeat to registry"""
        if not self.server_id:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.registry_url}/servers/{self.server_id}/heartbeat") as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(f"Heartbeat failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False

    async def start_heartbeat(self):
        """Start periodic heartbeat"""
        if self.heartbeat_task:
            return

        async def heartbeat_loop():
            while self.is_registered:
                try:
                    success = await self.send_heartbeat()
                    if not success:
                        logger.warning("Heartbeat failed, attempting re-registration")
                        success = await self.register_server()
                        if not success:
                            break
                    await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                except Exception as e:
                    logger.error(f"Heartbeat loop error: {e}")
                    await asyncio.sleep(30)

        self.heartbeat_task = asyncio.create_task(heartbeat_loop())

    async def stop_heartbeat(self):
        """Stop heartbeat and unregister"""
        self.is_registered = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None

        await self.unregister_server()
