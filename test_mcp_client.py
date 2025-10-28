#!/usr/bin/env python3
"""
Test MCP Client - Shows how to connect to and use the MCP server
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Any, Dict, Optional

DEFAULT_SERVER_CONFIG = {
    "command": "python3",
    "args": ["-m", "corporate_lxp_mcp.mcp_server.main"],
    "env": {
        "CORPORATE_LXP_REGISTRY_HOST": "localhost",
        "CORPORATE_LXP_REGISTRY_PORT": "9000",
        "CORPORATE_LXP_LOG_LEVEL": "INFO",
        "PYTHONPATH": ".",
    },
}

class MCPClient:
    """Simple MCP client that connects to MCP server via subprocess"""
    
    def __init__(self, server_config: Dict[str, Any]):
        self.config = server_config
        self.process = None
        self._next_id = 1
        self._stream_tasks: list[asyncio.Task] = []

    def _next_request_id(self) -> int:
        """Generate the next JSON-RPC request identifier."""
        request_id = self._next_id
        self._next_id += 1
        return request_id

    async def start_server(self):
        """Start the MCP server as a subprocess"""
        print("🚀 Starting MCP server...")
        
        # Use python3 instead of python for macOS
        command = "python3" if self.config["command"] == "python" else self.config["command"]
        cmd = [command] + self.config["args"]
        configured_env = self.config.get("env", {}) or {}
        raw_env = {str(k): str(v) for k, v in configured_env.items()}
        env = os.environ.copy()
        env.update(raw_env)

        # Start the server process
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        print(f"✅ Server started with PID: {self.process.pid}")
        self._start_stream_task(self.process.stderr, "STDERR")
        await asyncio.sleep(0.1)
        if self.process.returncode is not None:
            stderr_output = await self.process.stderr.read()
            raise RuntimeError(
                f"MCP server exited immediately with code {self.process.returncode}:\n{stderr_output.decode()}"
            )
        return self.process
        
    async def initialize(self):
        """Initialize MCP connection"""
        if not self.process:
            await self.start_server()

        request_id = self._next_request_id()
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        print("📡 Sending initialize request...")
        await self._send_request(init_request)
        response = await self._read_response(expected_id=request_id)
        print(f"✅ Initialize response: {response}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self._send_request(initialized_notification)
        print("✅ Connection initialized")
        
    async def list_tools(self):
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list"
        }
        
        print("🔧 Listing available tools...")
        await self._send_request(request)
        response = await self._read_response(expected_id=request["id"])
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            return tools
        else:
            print("❌ Failed to get tools")
            return None
            
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """Call a specific tool"""
        if arguments is None:
            arguments = {}
            
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        print(f"🔨 Calling tool: {tool_name} with args: {arguments}")
        await self._send_request(request)
        response = await self._read_response(expected_id=request["id"])
        
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"]
            print(f"✅ Tool result:")
            for item in content:
                if item.get("type") == "text":
                    print(f"  📄 {item['text']}")
            return response["result"]
        else:
            print(f"❌ Tool call failed: {response}")
            return None
            
    async def _send_request(self, request: Dict[str, Any]):
        """Send JSON-RPC request to server"""
        if not self.process:
            raise RuntimeError("Server not started")

        message = json.dumps(request, ensure_ascii=False) + "\n"
        self.process.stdin.write(message.encode("utf-8"))
        await self.process.stdin.drain()

    async def _read_message(self) -> Dict[str, Any]:
        """Read a single JSON-RPC message from stdout."""
        if not self.process:
            raise RuntimeError("Server not started")

        line = await self.process.stdout.readline()
        if not line:
            raise RuntimeError("Server closed connection")

        try:
            return json.loads(line.decode("utf-8").strip())
        except json.JSONDecodeError as exc:
            print(f"❌ Failed to decode response line: {line!r}")
            raise exc

    async def _read_response(self, expected_id: Optional[int] = None) -> Dict[str, Any]:
        """Read MCP responses, skipping notifications until the expected one arrives."""
        while True:
            try:
                message = await asyncio.wait_for(self._read_message(), timeout=15)
            except asyncio.TimeoutError as exc:
                raise RuntimeError("Timed out waiting for server response") from exc
            if expected_id is None:
                if "id" in message or "error" in message:
                    return message
            else:
                if message.get("id") == expected_id or "error" in message:
                    return message

            method = message.get("method")
            if method:
                print(f"ℹ️  Received notification: {method}")
            else:
                print(f"ℹ️  Skipping unexpected message: {message}")
            
    async def close(self):
        """Close the server connection"""
        if self.process:
            print("🛑 Closing MCP server...")
            self.process.terminate()
            await self.process.wait()
            print("✅ Server closed")
        for task in self._stream_tasks:
            task.cancel()
        self._stream_tasks.clear()

    def _start_stream_task(self, stream: asyncio.StreamReader, label: str) -> None:
        async def _reader() -> None:
            try:
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    text = line.decode(errors="replace").rstrip()
                    if text:
                        print(f"[{label}] {text}")
            except asyncio.CancelledError:
                pass

        self._stream_tasks.append(asyncio.create_task(_reader()))

async def test_mcp_connection():
    """Test the MCP client connection"""
    print("🧪 Testing MCP Connection...")
    
    # Get the server config from registry
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/mcp-config")
            config_data = response.json()
            mcp_servers = config_data["mcpServers"]
            if not mcp_servers:
                raise ValueError("No MCP servers found in config")
            # Get the first available server
            server_name = list(mcp_servers.keys())[0]
            server_config = mcp_servers[server_name]
            print(f"✅ Using server: {server_name}")
            print(f"✅ Got server config: {server_config}")
    except Exception as e:
        print(f"❌ Failed to get config: {e}")
        print("ℹ️  Falling back to default local server configuration")
        server_config = DEFAULT_SERVER_CONFIG
        server_name = "default_local"
    
    # Create and use MCP client
    client = MCPClient(server_config)
    
    try:
        # Start and initialize
        await client.start_server()
        await client.initialize()
        
        # List tools
        tools = await client.list_tools()
        
        if tools:
            # Test a simple tool call
            print("\n🔨 Testing list_employees tool...")
            result = await client.call_tool("list_employees", {})
            
            print("\n🔨 Testing list_departments tool...")
            result = await client.call_tool("list_departments", {})
            
    except Exception as e:
        print(f"❌ Error during MCP connection: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
