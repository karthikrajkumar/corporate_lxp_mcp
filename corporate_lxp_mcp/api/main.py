"""FastAPI main application"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .employee_routes import router as employee_router
from .training_routes import router as training_router
from .department_routes import router as department_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Corporate LXP API",
        description="Learning Experience Platform API for Corporate Employee Management",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(employee_router, prefix="/api/v1/employees", tags=["employees"])
    app.include_router(training_router, prefix="/api/v1/training", tags=["training"])
    app.include_router(department_router, prefix="/api/v1/departments", tags=["departments"])

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"message": "Corporate LXP API", "version": "1.0.0"}

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "corporate-lxp-api"}

    return app


app = create_app()
