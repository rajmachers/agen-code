from fastapi import FastAPI

from app.routers.assessment import router as assessment_router
from app.routers.health import router as health_router
from app.routers.learning import router as learning_router
from app.routers.simulator import router as simulator_router

app = FastAPI(
    title="Coding Practice Orchestrator",
    description="AI-powered orchestration API for learning generation and coding assessments.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(learning_router)
app.include_router(assessment_router)
app.include_router(simulator_router)
