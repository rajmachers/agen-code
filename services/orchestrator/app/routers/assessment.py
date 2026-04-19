from typing import Literal

from fastapi import APIRouter

from app.core.clients import generate_with_ollama, run_assessment, sync_to_moodle
from app.core.config import settings
from app.schemas import (
    EvaluateSubmissionRequest,
    EvaluateSubmissionResponse,
    MoodleSyncRequest,
)

router = APIRouter(prefix="/assessment", tags=["assessment"])


def _deterministic_feedback(test_pass_rate: float, execution_ms: int, memory_mb: int) -> str:
    if test_pass_rate < 0.5:
        correctness_tip = "Fix failing tests before optimization."
    elif test_pass_rate < 0.8:
        correctness_tip = "Cover edge cases to raise pass rate."
    else:
        correctness_tip = "Maintain correctness with focused refactors."

    if execution_ms > 1200:
        performance_tip = "Reduce algorithmic complexity in hot paths."
    elif execution_ms > 700:
        performance_tip = "Cache repeated computations where possible."
    else:
        performance_tip = "Execution speed is good; keep it stable."

    if memory_mb > 160:
        memory_tip = "Trim large allocations and intermediate objects."
    elif memory_mb > 100:
        memory_tip = "Review data structures for memory efficiency."
    else:
        memory_tip = "Memory usage is healthy; avoid regressions."

    return "\n".join([correctness_tip, performance_tip, memory_tip])


@router.post("/evaluate", response_model=EvaluateSubmissionResponse)
async def evaluate_submission(
    payload: EvaluateSubmissionRequest,
    mode: Literal["deterministic", "llm", "auto"] = "deterministic",
) -> EvaluateSubmissionResponse:
    runner_result = await run_assessment(payload.model_dump())

    ai_feedback = _deterministic_feedback(
        test_pass_rate=runner_result["test_pass_rate"],
        execution_ms=runner_result["execution_ms"],
        memory_mb=runner_result["memory_mb"],
    )

    use_llm = mode == "llm" or (mode == "auto" and settings.assessment_use_ollama)
    if use_llm:
        prompt = (
            "Return 3 improvements. "
            "One line each, max 6 words. "
            "Cover correctness, speed, memory. "
            f"pass_rate={runner_result['test_pass_rate']}, "
            f"execution_ms={runner_result['execution_ms']}, "
            f"memory_mb={runner_result['memory_mb']}. "
            "No intro or explanation."
        )
        llm_feedback = await generate_with_ollama(
            prompt,
            timeout_seconds=settings.assessment_ollama_timeout_seconds,
            num_predict=settings.assessment_ollama_num_predict,
            max_chars=settings.assessment_ollama_max_chars,
            stop_after_lines=3,
        )
        if llm_feedback:
            ai_feedback = llm_feedback

    score = round(runner_result["test_pass_rate"] * 100, 2)
    plagiarism_risk = "low" if runner_result["test_pass_rate"] >= 0.6 else "review"

    response = EvaluateSubmissionResponse(
        assignment_id=payload.assignment_id,
        learner_id=payload.learner_id,
        score=score,
        test_pass_rate=runner_result["test_pass_rate"],
        execution_ms=runner_result["execution_ms"],
        memory_mb=runner_result["memory_mb"],
        ai_feedback=ai_feedback,
        plagiarism_risk=plagiarism_risk,
    )

    await sync_to_moodle(
        MoodleSyncRequest(
            learner_id=payload.learner_id,
            assignment_id=payload.assignment_id,
            score=score,
            feedback=response.ai_feedback,
        ).model_dump()
    )
    return response
