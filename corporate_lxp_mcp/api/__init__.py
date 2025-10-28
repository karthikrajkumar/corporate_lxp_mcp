"""API layer for Corporate LXP platform"""

from .main import app
from .employee_routes import router as employee_router

__all__ = ["app", "employee_router"]
