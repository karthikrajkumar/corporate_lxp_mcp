"""MCP Server implementation for Corporate LXP platform following SOLID principles"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent
)

from ..services.employee_service import EmployeeService
from ..services.data_service import DataService
from ..services.registration_service import RegistrationService

logger = logging.getLogger(__name__)


class CorporateLXPServer:
    """MCP Server for Corporate LXP platform"""

    def __init__(self):
        """Initialize the MCP server"""
        self.server = Server("corporate-lxp-mcp")
        self.employee_service = EmployeeService()
        self.data_service = DataService()
        self.registration_service = RegistrationService()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="list_employees",
                        description="List all corporate employees with optional filtering",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "department": {
                                    "type": "string",
                                    "description": "Filter by department ID"
                                },
                                "role": {
                                    "type": "string",
                                    "description": "Filter by employee role"
                                },
                                "manager": {
                                    "type": "string",
                                    "description": "Filter by manager ID"
                                },
                                "search": {
                                    "type": "string",
                                    "description": "Search by name or email"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_employee",
                        description="Get employee details by ID or email",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "employee_id": {
                                    "type": "string",
                                    "description": "Employee ID"
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Employee email address"
                                }
                            },
                            "oneOf": [
                                {"required": ["employee_id"]},
                                {"required": ["email"]}
                            ]
                        }
                    ),
                    Tool(
                        name="create_employee",
                        description="Create a new employee",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "email": {"type": "string", "format": "email"},
                                "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
                                "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
                                "department_id": {"type": "string"},
                                "role": {
                                    "type": "string",
                                    "enum": ["executive", "manager", "team_lead", "individual_contributor", "hr", "finance"]
                                },
                                "manager_id": {"type": "string"},
                                "location": {"type": "string"},
                                "phone": {"type": "string"}
                            },
                            "required": ["email", "first_name", "last_name", "department_id", "role", "location"]
                        }
                    ),
                    Tool(
                        name="update_employee",
                        description="Update employee information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "employee_id": {"type": "string"},
                                "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
                                "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
                                "department_id": {"type": "string"},
                                "role": {
                                    "type": "string",
                                    "enum": ["executive", "manager", "team_lead", "individual_contributor", "hr", "finance"]
                                },
                                "manager_id": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["active", "inactive", "on_leave"]
                                },
                                "location": {"type": "string"},
                                "phone": {"type": "string"}
                            },
                            "required": ["employee_id"]
                        }
                    ),
                    Tool(
                        name="delete_employee",
                        description="Delete an employee",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "employee_id": {"type": "string"}
                            },
                            "required": ["employee_id"]
                        }
                    ),
                    Tool(
                        name="get_employee_training",
                        description="Get employee training assignments and progress",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "employee_id": {"type": "string"}
                            },
                            "required": ["employee_id"]
                        }
                    ),
                    Tool(
                        name="get_employee_skills",
                        description="Get employee skill assessments",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "employee_id": {"type": "string"}
                            },
                            "required": ["employee_id"]
                        }
                    ),
                    Tool(
                        name="get_department_employees",
                        description="Get all employees in a department",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "department_id": {"type": "string"}
                            },
                            "required": ["department_id"]
                        }
                    ),
                    Tool(
                        name="update_training_progress",
                        description="Update training progress for an employee",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "assignment_id": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["assigned", "in_progress", "completed", "failed", "expired"]
                                },
                                "score": {"type": "integer", "minimum": 0, "maximum": 100}
                            },
                            "required": ["assignment_id", "status"]
                        }
                    ),
                    Tool(
                        name="list_departments",
                        description="List all departments",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="list_training_programs",
                        description="List all available training programs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "training_type": {
                                    "type": "string",
                                    "enum": ["onboarding", "compliance", "technical", "leadership", "soft_skills", "safety"]
                                },
                                "department": {"type": "string"}
                            }
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """Handle tool calls"""
            if name == "list_employees":
                return await self._list_employees(arguments)
            if name == "get_employee":
                return await self._get_employee(arguments)
            if name == "create_employee":
                return await self._create_employee(arguments)
            if name == "update_employee":
                return await self._update_employee(arguments)
            if name == "delete_employee":
                return await self._delete_employee(arguments)
            if name == "get_employee_training":
                return await self._get_employee_training(arguments)
            if name == "get_employee_skills":
                return await self._get_employee_skills(arguments)
            if name == "get_department_employees":
                return await self._get_department_employees(arguments)
            if name == "update_training_progress":
                return await self._update_training_progress(arguments)
            if name == "list_departments":
                return await self._list_departments(arguments)
            if name == "list_training_programs":
                return await self._list_training_programs(arguments)

            raise ValueError(f"Unknown tool: {name}")

    async def _list_employees(self, args: Dict[str, Any]) -> List[TextContent]:
        """List employees with filtering"""
        employees = self.employee_service.get_all_employees()
        
        if args.get("department"):
            employees = [emp for emp in employees if emp.department_id == args["department"]]
        
        if args.get("role"):
            employees = [emp for emp in employees if emp.role.value == args["role"]]
        
        if args.get("manager"):
            employees = [emp for emp in employees if emp.manager_id == args["manager"]]
        
        if args.get("search"):
            employees = self.employee_service.search_employees(args["search"])
        
        return [
            TextContent(
                type="text",
                text=json.dumps([emp.dict() for emp in employees], default=str, indent=2)
            )
        ]

    async def _get_employee(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get employee by ID or email"""
        if args.get("employee_id"):
            employee = self.employee_service.get_employee_by_id(args["employee_id"])
        elif args.get("email"):
            employee = self.employee_service.get_employee_by_email(args["email"])
        else:
            raise ValueError("Either employee_id or email must be provided")
        
        if not employee:
            raise ValueError("Employee not found")
        
        return [
            TextContent(
                type="text",
                text=json.dumps(employee.dict(), default=str, indent=2)
            )
        ]

    async def _create_employee(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create new employee"""
        from corporate_lxp_mcp.models.employee import EmployeeCreate
        
        employee_create = EmployeeCreate(**args)
        employee = self.employee_service.create_employee(employee_create)
        
        return [
            TextContent(
                type="text",
                text=f"Employee created successfully:\n{json.dumps(employee.dict(), default=str, indent=2)}"
            )
        ]

    async def _update_employee(self, args: Dict[str, Any]) -> List[TextContent]:
        """Update employee"""
        from corporate_lxp_mcp.models.employee import EmployeeUpdate
        
        employee_id = args.pop("employee_id")
        employee_update = EmployeeUpdate(**args)
        employee = self.employee_service.update_employee(employee_id, employee_update)
        
        if not employee:
            raise ValueError("Employee not found")
        
        return [
            TextContent(
                type="text",
                text=f"Employee updated successfully:\n{json.dumps(employee.dict(), default=str, indent=2)}"
            )
        ]

    async def _delete_employee(self, args: Dict[str, Any]) -> List[TextContent]:
        """Delete employee"""
        success = self.employee_service.delete_employee(args["employee_id"])
        
        if not success:
            raise ValueError("Employee not found")
        
        return [TextContent(type="text", text="Employee deleted successfully")]

    async def _get_employee_training(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get employee training assignments"""
        assignments = self.employee_service.get_employee_training_assignments(args["employee_id"])
        
        return [
            TextContent(
                type="text",
                text=json.dumps([assign.dict() for assign in assignments], default=str, indent=2)
            )
        ]

    async def _get_employee_skills(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get employee skill assessments"""
        assessments = self.employee_service.get_employee_skill_assessments(args["employee_id"])
        
        return [
            TextContent(
                type="text",
                text=json.dumps([assess.dict() for assess in assessments], default=str, indent=2)
            )
        ]

    async def _get_department_employees(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get department employees"""
        employees = self.employee_service.get_employees_by_department(args["department_id"])
        
        return [
            TextContent(
                type="text",
                text=json.dumps([emp.dict() for emp in employees], default=str, indent=2)
            )
        ]

    async def _update_training_progress(self, args: Dict[str, Any]) -> List[TextContent]:
        """Update training progress"""
        from corporate_lxp_mcp.models.training import TrainingStatus
        
        assignment_id = args["assignment_id"]
        status = TrainingStatus(args["status"])
        score = args.get("score")
        
        assignment = self.data_service.training_assignments.get(assignment_id)
        if not assignment:
            raise ValueError("Training assignment not found")
        
        assignment.status = status
        if score is not None:
            assignment.score = score
        
        if status == TrainingStatus.COMPLETED:
            from datetime import datetime
            assignment.completion_date = datetime.now()
        
        return [
            TextContent(
                type="text",
                text=f"Training progress updated:\n{json.dumps(assignment.dict(), default=str, indent=2)}"
            )
        ]

    async def _list_departments(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all departments"""
        departments = list(self.data_service.departments.values())
        
        return [
            TextContent(
                type="text",
                text=json.dumps([dept.dict() for dept in departments], default=str, indent=2)
            )
        ]

    async def _list_training_programs(self, args: Dict[str, Any]) -> List[TextContent]:
        """List training programs"""
        programs = list(self.data_service.training_programs.values())
        
        if args.get("training_type"):
            programs = [prog for prog in programs if prog.training_type.value == args["training_type"]]
        
        if args.get("department"):
            programs = [prog for prog in programs if args["department"] in prog.department_ids]
        
        return [
            TextContent(
                type="text",
                text=json.dumps([prog.dict() for prog in programs], default=str, indent=2)
            )
        ]

    async def run(self):
        """Run the MCP server."""

        logger.info("Registering MCP server with registry...")
        registration_success = await self.registration_service.register_server()

        if registration_success:
            logger.info("MCP server registered successfully")
            await self.registration_service.start_heartbeat()
        else:
            logger.warning("Failed to register with registry, continuing anyway")

        try:
            try:
                async with stdio_server() as (read_stream, write_stream):
                    init_options = self.server.create_initialization_options()
                    await self.server.run(
                        read_stream,
                        write_stream,
                        initialization_options=init_options,
                    )
            except Exception as exc:
                if isinstance(exc, asyncio.CancelledError):
                    raise
                logger.warning(f"STDIO session ended with error: {exc}. Entering idle mode.")

            logger.info("STDIO session finished. Keeping server registered and idle.")
            await self._idle_loop()
        except asyncio.CancelledError:
            logger.info("MCP server cancellation requested")
            raise
        finally:
            await self.registration_service.stop_heartbeat()
            logger.info("MCP server shutdown complete")

    async def _idle_loop(self) -> None:
        """Keep process alive so heartbeat can continue until termination."""
        while True:
            await asyncio.sleep(30)
