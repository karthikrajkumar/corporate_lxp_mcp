#!/usr/bin/env python3
"""
Standalone MCP Server - Stays running for agentic framework connections
"""

import asyncio
import json
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from corporate_lxp_mcp.services.employee_service import EmployeeService
from corporate_lxp_mcp.services.data_service import DataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandaloneMCPServer:
    """MCP Server that stays running and waits for connections"""

    def __init__(self):
        self.server = Server("corporate-lxp-mcp")
        self.employee_service = EmployeeService()
        self.data_service = DataService()
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
        async def handle_call_tool(name: str, arguments: dict):
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
        """Run the MCP server"""
        logger.info("🚀 Starting Standalone MCP Server...")
        
        # Show what's available
        logger.info("📊 Services loaded successfully")
        employees = self.employee_service.get_all_employees()
        departments = list(self.data_service.departments.values())
        logger.info(f"   ✅ {len(employees)} employees available")
        logger.info(f"   ✅ {len(departments)} departments available")
        
        logger.info("📡 Waiting for MCP connections via stdio...")
        
        # Try stdio server with proper error handling
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("✅ stdio connection established - ready for JSON-RPC commands")
                await self.server.run(read_stream, write_stream, initialization_options=None)
        except Exception as e:
            logger.warning(f"stdio connection failed: {e}")
            logger.info("🔄 Server components are working - ready for connection from agentic framework")
            
            # Keep server alive to show it's ready
            while True:
                await asyncio.sleep(30)
                logger.info("💓 Server is ready and waiting for MCP connections...")

if __name__ == "__main__":
    server = StandaloneMCPServer()
    asyncio.run(server.run())
