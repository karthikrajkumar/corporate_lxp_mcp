"""Data service providing mock data following SOLID principles"""

from datetime import datetime, timedelta
from typing import Dict, List
from uuid import uuid4

from ..models.employee import Employee, EmployeeRole, EmployeeStatus
from ..models.department import Department
from ..models.training import TrainingProgram, TrainingType, TrainingAssignment, TrainingStatus
from ..models.skills import Skill, SkillLevel, SkillCategory


class DataService:
    """Singleton data service providing in-memory mock data storage"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(DataService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize data if not already done"""
        if not self._initialized:
            self._initialize_data()
            DataService._initialized = True

    def _initialize_data(self):
        """Initialize mock data for the corporate LXP platform"""
        
        # Departments
        self.departments: Dict[str, Department] = {
            "eng": Department(
                id="eng",
                name="Engineering",
                description="Software development and technology infrastructure",
                location="San Francisco",
                budget_code="ENG-2024"
            ),
            "sales": Department(
                id="sales",
                name="Sales",
                description="Revenue generation and client relationships",
                location="New York",
                budget_code="SLS-2024"
            ),
            "marketing": Department(
                id="marketing",
                name="Marketing",
                description="Brand management and customer acquisition",
                location="Los Angeles",
                budget_code="MKT-2024"
            ),
            "hr": Department(
                id="hr",
                name="Human Resources",
                description="Talent management and employee relations",
                location="Chicago",
                budget_code="HR-2024"
            ),
            "finance": Department(
                id="finance",
                name="Finance",
                description="Financial planning and accounting",
                location="Boston",
                budget_code="FIN-2024"
            ),
            "ops": Department(
                id="ops",
                name="Operations",
                description="Business operations and process improvement",
                location="Austin",
                budget_code="OPS-2024"
            )
        }

        # Employees
        self.employees: Dict[str, Employee] = {}
        self._create_employees()

        # Training Programs
        self.training_programs: Dict[str, TrainingProgram] = {
            "onboarding": TrainingProgram(
                id="onboarding",
                title="Company Onboarding",
                description="Introduction to company culture, policies, and systems",
                training_type=TrainingType.ONBOARDING,
                duration_hours=8,
                is_mandatory=True,
                expiry_months=12
            ),
            "leadership": TrainingProgram(
                id="leadership",
                title="Leadership Excellence",
                description="Develop leadership skills for managers",
                training_type=TrainingType.LEADERSHIP,
                duration_hours=16,
                required_for_roles=["manager", "team_lead", "executive"]
            ),
            "security": TrainingProgram(
                id="security",
                title="Information Security",
                description="Security best practices and compliance",
                training_type=TrainingType.COMPLIANCE,
                duration_hours=4,
                is_mandatory=True,
                expiry_months=6
            ),
            "python": TrainingProgram(
                id="python",
                title="Python Programming",
                description="Python programming fundamentals and advanced concepts",
                training_type=TrainingType.TECHNICAL,
                duration_hours=24,
                department_ids=["eng"]
            ),
            "communication": TrainingProgram(
                id="communication",
                title="Effective Communication",
                description="Improve interpersonal communication skills",
                training_type=TrainingType.SOFT_SKILLS,
                duration_hours=8
            )
        }

        # Training Assignments
        self.training_assignments: Dict[str, TrainingAssignment] = {}
        self._create_training_assignments()

        # Skill Assessments
        self.skill_assessments: Dict[str, SkillAssessment] = {}

        # Skills
        self.skills: Dict[str, Skill] = {
            "python": Skill(
                id="python",
                name="Python Programming",
                description="Proficiency in Python programming language",
                category=SkillCategory.TECHNICAL,
                relevant_roles=["individual_contributor", "team_lead", "manager"]
            ),
            "leadership": Skill(
                id="leadership",
                name="Leadership",
                description="Ability to lead teams and projects effectively",
                category=SkillCategory.LEADERSHIP,
                relevant_roles=["manager", "team_lead", "executive"]
            ),
            "communication": Skill(
                id="communication",
                name="Communication",
                description="Effective verbal and written communication",
                category=SkillCategory.COMMUNICATION,
                relevant_roles=["manager", "team_lead", "hr", "sales"]
            ),
            "project_mgmt": Skill(
                id="project_mgmt",
                name="Project Management",
                description="Project planning and execution skills",
                category=SkillCategory.PROJECT_MANAGEMENT,
                relevant_roles=["manager", "team_lead"]
            ),
            "data_analysis": Skill(
                id="data_analysis",
                name="Data Analysis",
                description="Ability to analyze and interpret data",
                category=SkillCategory.ANALYTICAL,
                relevant_roles=["individual_contributor", "manager"]
            )
        }

    def _create_employees(self):
        """Create sample employees"""
        employees_data = [
            {
                "id": "emp001",
                "email": "john.smith@company.com",
                "first_name": "John",
                "last_name": "Smith",
                "department_id": "eng",
                "role": EmployeeRole.MANAGER,
                "manager_id": None,
                "hire_date": datetime(2020, 1, 15),
                "location": "San Francisco"
            },
            {
                "id": "emp002",
                "email": "jane.doe@company.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "department_id": "eng",
                "role": EmployeeRole.TEAM_LEAD,
                "manager_id": "emp001",
                "hire_date": datetime(2020, 6, 1),
                "location": "San Francisco"
            },
            {
                "id": "emp003",
                "email": "mike.johnson@company.com",
                "first_name": "Mike",
                "last_name": "Johnson",
                "department_id": "eng",
                "role": EmployeeRole.INDIVIDUAL_CONTRIBUTOR,
                "manager_id": "emp002",
                "hire_date": datetime(2021, 3, 10),
                "location": "San Francisco"
            },
            {
                "id": "emp004",
                "email": "sarah.wilson@company.com",
                "first_name": "Sarah",
                "last_name": "Wilson",
                "department_id": "sales",
                "role": EmployeeRole.MANAGER,
                "manager_id": None,
                "hire_date": datetime(2019, 8, 20),
                "location": "New York"
            },
            {
                "id": "emp005",
                "email": "robert.brown@company.com",
                "first_name": "Robert",
                "last_name": "Brown",
                "department_id": "hr",
                "role": EmployeeRole.HR,
                "manager_id": None,
                "hire_date": datetime(2018, 4, 5),
                "location": "Chicago"
            }
        ]

        for emp_data in employees_data:
            self.employees[emp_data["id"]] = Employee(**emp_data)

    def _create_training_assignments(self):
        """Create sample training assignments"""
        assignments = [
            {
                "id": "ta001",
                "employee_id": "emp001",
                "training_program_id": "leadership",
                "assigned_by": "emp005",
                "status": TrainingStatus.COMPLETED,
                "completion_date": datetime.now() - timedelta(days=30),
                "score": 95
            },
            {
                "id": "ta002",
                "employee_id": "emp003",
                "training_program_id": "python",
                "assigned_by": "emp002",
                "status": TrainingStatus.IN_PROGRESS
            },
            {
                "id": "ta003",
                "employee_id": "emp004",
                "training_program_id": "communication",
                "assigned_by": "emp005",
                "status": TrainingStatus.ASSIGNED
            }
        ]

        for assignment_data in assignments:
            self.training_assignments[assignment_data["id"]] = TrainingAssignment(**assignment_data)
