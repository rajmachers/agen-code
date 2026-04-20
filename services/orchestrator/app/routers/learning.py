from fastapi import APIRouter, Depends

from app.core.clients import generate_with_ollama
from app.core.config import settings
from app.core.security import AuthContext, require_roles
from app.schemas import LearningModuleRequest, LearningModuleResponse

router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("/generate", response_model=LearningModuleResponse)
async def generate_learning_module(
    payload: LearningModuleRequest,
    _auth: AuthContext = Depends(require_roles("tenant_admin", "teacher", "sme", "candidate")),
) -> LearningModuleResponse:
    prompt = (
        "You are a concise programming tutor. "
        "Return plain text with headings: Roadmap, Quiz, Summary. "
        "Keep each section brief and practical. "
        f"Topic: {payload.topic}. Level: {payload.level}. Goals: {', '.join(payload.goals) or 'none'}. "
        "No preamble."
    )
    llm_text = await generate_with_ollama(
        prompt,
        timeout_seconds=settings.learning_ollama_timeout_seconds,
        num_predict=settings.learning_ollama_num_predict,
        max_chars=settings.learning_ollama_max_chars,
    )

    # MVP parser fallback: deterministic structure even if model formatting varies.
    roadmap = [
        f"Understand fundamentals of {payload.topic}",
        f"Implement guided examples for {payload.topic}",
        f"Solve timed practice challenges on {payload.topic}",
    ]
    quiz = [
        {"question": f"What is the core idea of {payload.topic}?", "type": "short_answer"},
        {"question": f"When should you use {payload.topic}?", "type": "short_answer"},
        {"question": f"Name a common pitfall in {payload.topic}.", "type": "short_answer"},
        {"question": f"How do you test {payload.topic} implementations?", "type": "short_answer"},
        {"question": f"How do performance constraints affect {payload.topic}?", "type": "short_answer"},
    ]
    summary = llm_text[:600] if llm_text else f"Learner-focused module for {payload.topic}."

    return LearningModuleResponse(roadmap=roadmap, quiz=quiz, summary=summary)
