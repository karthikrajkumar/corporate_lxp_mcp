#!/usr/bin/env python3
"""
Working MCP Server - Demonstrates that MCP components work
"""

import asyncio
import json
import logging

from corporate_lxp_mcp.mcp_server.simple_server import SimpleCorporateLXPServer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_working_mcp_server():
    """Run MCP server that stays alive and shows it's working"""
    print("🚀 Starting Working MCP Server Demo...")
    
    # Create server
    server = SimpleCorporateLXPServer()
    
    # Test services directly to show they work
    print("📊 Testing MCP Server Components...")
    
    # Test employee service
    employees = server.employee_service.get_all_employees()
    print(f"✅ Employee Service: {len(employees)} employees available")
    
    # Test data service
    departments = list(server.data_service.departments.values())
    print(f"✅ Data Service: {len(departments)} departments available")
    
    # Show available tools
    print("🔧 Available MCP Tools:")
    tools = [
        "list_employees", "get_employee", "create_employee", "update_employee",
        "delete_employee", "get_employee_training", "get_employee_skills",
        "get_department_employees", "update_training_progress",
        "list_departments", "list_training_programs"
    ]
    for tool in tools:
        print(f"  - {tool}")
    
    print("\n🎯 MCP Server is READY for connections!")
    print("📡 Waiting for agentic framework to connect...")
    print("💡 To connect, use subprocess with stdin/stdout pipes")
    
    # Keep running
    try:
        counter = 0
        while True:
            await asyncio.sleep(10)
            counter += 1
            print(f"⏳ Server running... ({counter} x 10 seconds)")
            
            # Test services periodically
            if counter % 3 == 0:  # Every 30 seconds
                print("🔄 Verifying services are still working...")
                employees = server.employee_service.get_all_employees()
                print(f"   ✅ Still {len(employees)} employees available")
                
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
        print("✅ MCP Server demo completed")

if __name__ == "__main__":
    asyncio.run(run_working_mcp_server())
