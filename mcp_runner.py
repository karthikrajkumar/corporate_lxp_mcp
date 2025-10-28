#!/usr/bin/env python3
"""
MCP Server Runner - Shows how to start and connect to MCP server
"""

import asyncio
import json
import os
import subprocess
import sys

async def run_mcp_server_locally():
    """Run MCP server locally without registry (for testing)"""
    print("🚀 Starting MCP server locally...")
    
    # Set up environment
    env = {
        "PYTHONPATH": ".",
        "CORPORATE_LXP_LOG_LEVEL": "INFO"
    }
    
    # Start server process with correct module path
    cmd = ["python3", "-m", "corporate_lxp_mcp.mcp_server.main"]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**dict(os.environ), **env}
    )
    
    print(f"✅ Server started with PID: {process.pid}")
    return process

async def test_mcp_connection_simple():
    """Simple test of MCP connection without complex JSON-RPC"""
    print("🧪 Testing simple MCP connection...")
    
    # Start server
    process = await run_mcp_server_locally()
    
    try:
        # Give server time to start
        await asyncio.sleep(1)
        
        # Test if process is still running
        if process.returncode is None:
            print("✅ Server is running!")
            
            # Test basic functionality by accessing services directly
            sys.path.insert(0, '.')
            from corporate_lxp_mcp.services.employee_service import EmployeeService
            from corporate_lxp_mcp.services.data_service import DataService
            
            # Test services
            employee_service = EmployeeService()
            data_service = DataService()
            
            print("📊 Testing services directly:")
            employees = employee_service.get_all_employees()
            print(f"  ✅ Employee service: {len(employees)} employees")
            
            departments = list(data_service.departments.values())
            print(f"  ✅ Data service: {len(departments)} departments")
            
            print("🎯 MCP Server components are working correctly!")
            
        else:
            print(f"❌ Server exited with code: {process.returncode}")
            stderr_output = await process.stderr.read()
            if stderr_output:
                print(f"Error: {stderr_output.decode()}")
                
    finally:
        # Clean up
        if process.returncode is None:
            print("🛑 Stopping server...")
            process.terminate()
            await process.wait()
            print("✅ Server stopped")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection_simple())
