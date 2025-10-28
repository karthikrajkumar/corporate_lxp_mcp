"""Training API routes following SOLID principles"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models.training import TrainingProgram, TrainingAssignment, TrainingStatus
from ..services.employee_service import EmployeeService
from ..services.data_service import DataService


router = APIRouter()
employee_service = EmployeeService()
data_service = DataService()


@router.get("/programs", response_model=List[TrainingProgram])
async def get_training_programs(
    training_type: Optional[str] = Query(None, description="Filter by training type"),
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get all training programs"""
    programs = list(data_service.training_programs.values())
    
    if training_type:
        programs = [prog for prog in programs if prog.training_type.value == training_type]
    
    if department:
        programs = [prog for prog in programs if department in prog.department_ids]
    
    return programs


@router.get("/programs/{program_id}", response_model=TrainingProgram)
async def get_training_program(program_id: str):
    """Get training program by ID"""
    program = data_service.training_programs.get(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Training program not found")
    return program


@router.get("/assignments", response_model=List[TrainingAssignment])
async def get_training_assignments(
    employee: Optional[str] = Query(None, description="Filter by employee ID"),
    program: Optional[str] = Query(None, description="Filter by program ID"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get all training assignments"""
    assignments = list(data_service.training_assignments.values())
    
    if employee:
        assignments = [assign for assign in assignments if assign.employee_id == employee]
    
    if program:
        assignments = [assign for assign in assignments if assign.training_program_id == program]
    
    if status:
        assignments = [assign for assign in assignments if assign.status.value == status]
    
    return assignments


@router.get("/assignments/{assignment_id}", response_model=TrainingAssignment)
async def get_training_assignment(assignment_id: str):
    """Get training assignment by ID"""
    assignment = data_service.training_assignments.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Training assignment not found")
    return assignment


@router.post("/assignments/{assignment_id}/progress", response_model=TrainingAssignment)
async def update_training_progress(
    assignment_id: str,
    status: TrainingStatus,
    score: Optional[int] = None
):
    """Update training assignment progress"""
    assignment = data_service.training_assignments.get(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Training assignment not found")
    
    assignment.status = status
    if score is not None:
        assignment.score = score
    
    if status == TrainingStatus.COMPLETED:
        from datetime import datetime
        assignment.completion_date = datetime.now()
    
    return assignment
