from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.assessment import router as assessment_router
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.connectors import router as connectors_router
from app.routers.delivery import router as delivery_router
from app.routers.evidence import router as evidence_router
from app.routers.ghost import router as ghost_router
from app.routers.health import router as health_router
from app.routers.learning import router as learning_router
from app.routers.authoring import router as authoring_router
from app.routers.simulator import router as simulator_router

app = FastAPI(
    title="Coding Practice Orchestrator",
    description="AI-powered orchestration API for learning generation and coding assessments.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(authoring_router)
app.include_router(learning_router)
app.include_router(assessment_router)
app.include_router(delivery_router)
app.include_router(evidence_router)
app.include_router(simulator_router)
app.include_router(ghost_router)
app.include_router(connectors_router)
