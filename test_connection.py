#!/usr/bin/env python3
"""
Test MCP Connection - Shows exactly how to connect to the MCP server
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_connection():
    """Test connecting to MCP server via subprocess"""
    print("🧪 Testing MCP Server Connection...")
    
    # Start the MCP server with stdin pipe
    print("🚀 Starting MCP server...")
    process = await asyncio.create_subprocess_exec(
        "python3", "mcp_server_standalone.py",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**dict(os.environ), "PYTHONPATH": "."}
    )
    
    print(f"✅ Server started with PID: {process.pid}")
    
    try:
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        # Check if process is still running
        if process.returncode is None:
            print("✅ Server is running!")
            
            # Get stderr to see startup messages
            stderr_data = await process.stderr.read()
            if stderr_data:
                print(f"📋 Server logs:\n{stderr_data.decode()}")
            
            print("🎯 MCP Server is ready for connections!")
            print("💡 The server would wait for JSON-RPC commands via stdin")
            
            # Test services directly
            sys.path.insert(0, '.')
            from corporate_lxp_mcp.services.employee_service import EmployeeService
            
            employee_service = EmployeeService()
            employees = employee_service.get_all_employees()
            print(f"📊 Services working: {len(employees)} employees available")
            
        else:
            print(f"❌ Server exited with code: {process.returncode}")
            stderr_data = await process.stderr.read()
            if stderr_data:
                print(f"Error: {stderr_data.decode()}")
                
    finally:
        # Clean up
        if process.returncode is None:
            print("🛑 Stopping server...")
            process.terminate()
            await process.wait()
            print("✅ Server stopped")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
