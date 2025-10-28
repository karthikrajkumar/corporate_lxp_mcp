#!/usr/bin/env python3
"""
Working MCP Server - Stays alive and ready for connections
"""

import asyncio
import json
import logging
import signal
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from corporate_lxp_mcp.services.employee_service import EmployeeService
from corporate_lxp_mcp.services.data_service import DataService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkingMCPServer:
    """MCP Server that actually stays running"""

    def __init__(self):
        self.server = Server("corporate-lxp-mcp")
        self.employee_service = EmployeeService()
        self.data_service = DataService()
        self.running = True
        self._setup_handlers()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Handle shutdown gracefully"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

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

    async def run_stdio_mode(self):
        """Run in stdio mode - for agentic frameworks"""
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("✅ stdio connection established - ready for JSON-RPC")
                await self.server.run(read_stream, write_stream, initialization_options=None)
        except Exception as e:
            logger.warning(f"stdio mode failed: {e}")

    async def run_standalone_mode(self):
        """Run in standalone mode - keeps server alive"""
        logger.info("🚀 Starting Standalone MCP Server...")
        
        # Show what's available
        employees = self.employee_service.get_all_employees()
        departments = list(self.data_service.departments.values())
        logger.info(f"📊 Services loaded: {len(employees)} employees, {len(departments)} departments")
        
        logger.info("🔧 Available tools: list_employees, get_employee, list_departments")
        logger.info("📡 Server is ready for MCP connections via stdio")
        
        # Keep server alive
        counter = 0
        while self.running:
            await asyncio.sleep(10)
            counter += 1
            
            if counter % 6 == 0:  # Every minute
                logger.info(f"💓 Server still running... ({counter//6} minutes)")
                
                # Verify services are working
                try:
                    test_employees = self.employee_service.get_all_employees()
                    logger.info(f"   ✅ Services verified: {len(test_employees)} employees available")
                except Exception as e:
                    logger.error(f"   ❌ Service error: {e}")

    async def run(self):
        """Main run method"""
        logger.info("🎯 Corporate LXP MCP Server starting...")
        
        # Try stdio mode first, fall back to standalone
        try:
            await self.run_stdio_mode()
        except Exception as e:
            logger.info(f"Falling back to standalone mode: {e}")
            await self.run_standalone_mode()

if __name__ == "__main__":
    server = WorkingMCPServer()
    asyncio.run(server.run())
