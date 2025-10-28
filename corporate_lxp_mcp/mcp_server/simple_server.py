"""Simplified MCP Server implementation"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ..services.employee_service import EmployeeService
from ..services.data_service import DataService
from ..services.registration_service import RegistrationService

logger = logging.getLogger(__name__)

class SimpleCorporateLXPServer:
    """Simplified MCP Server"""

    def __init__(self):
        self.server = Server("corporate-lxp-mcp")
        self.employee_service = EmployeeService()
        self.data_service = DataService()
        self.registration_service = RegistrationService()
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools():
            return [
                Tool(
                    name="list_employees",
                    description="List all corporate employees",
                    inputSchema={"type": "object"}
                ),
                Tool(
                    name="get_employee",
                    description="Get employee by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_id": {"type": "string"}
                        },
                        "required": ["employee_id"]
                    }
                ),
                Tool(
                    name="list_departments",
                    description="List all departments",
                    inputSchema={"type": "object"}
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            try:
                if name == "list_employees":
                    employees = self.employee_service.get_all_employees()
                    return [TextContent(
                        type="text",
                        text=json.dumps([emp.dict() for emp in employees], default=str, indent=2)
                    )]
                elif name == "get_employee":
                    employee = self.employee_service.get_employee_by_id(arguments["employee_id"])
                    if not employee:
                        return [TextContent(type="text", text="Employee not found")]
                    return [TextContent(
                        type="text",
                        text=json.dumps(employee.dict(), default=str, indent=2)
                    )]
                elif name == "list_departments":
                    departments = list(self.data_service.departments.values())
                    return [TextContent(
                        type="text",
                        text=json.dumps([dept.dict() for dept in departments], default=str, indent=2)
                    )]
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        # Try to register first (optional for stdio MCP servers)
        logger.info("Attempting to register with registry...")
        try:
            success = await self.registration_service.register_server()
            
            if success:
                logger.info("✅ Registered successfully")
                asyncio.create_task(self._heartbeat_loop())
            else:
                logger.warning("❌ Registration failed - continuing anyway")
        except Exception as e:
            logger.warning(f"⚠️ Registration attempt failed: {e} - continuing anyway")

        logger.info("Starting MCP server (stdio mode)...")
        
        # Check if we have proper stdin connection
        import sys
        
        # Try stdio_server first, but catch the case where stdin is not available
        try:
            logger.info("🚀 Starting MCP server (stdio mode)...")
            async with stdio_server() as (read_stream, write_stream):
                logger.info("✅ stdio connection established")
                await self.server.run(
                    read_stream,
                    write_stream,
                    initialization_options=None
                )
        except Exception as e:
            logger.warning(f"⚠️ stdio mode failed: {e}")
            
            # Fall back to demo mode
            logger.info("🚀 Running in demo mode - tools are ready for agentic framework!")
            logger.info("📋 Available tools: list_employees, get_employee, list_departments")
            logger.info("⏳ Server is registered and ready. Waiting for agentic framework to connect...")
            
            # Keep server running and registered
            try:
                while True:
                    await asyncio.sleep(30)
                    # Send periodic heartbeat to keep registration alive
                    if self.registration_service.is_registered:
                        try:
                            await self.registration_service.send_heartbeat()
                            logger.info("❤️ Heartbeat sent - server remains active")
                        except:
                            logger.warning("⚠️ Heartbeat failed")
            except KeyboardInterrupt:
                logger.info("🛑 Server shutdown requested")
            finally:
                try:
                    await self.registration_service.stop_heartbeat()
                except:
                    pass

    async def _heartbeat_loop(self):
        """Simple heartbeat loop"""
        while self.registration_service.is_registered:
            try:
                await self.registration_service.send_heartbeat()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break
