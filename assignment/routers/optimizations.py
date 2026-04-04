from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from database import get_conn
from registration.models.schemas import OptimizationRequest, OptimizationResponse
from badgelogic.score_service import update_user_score

router = APIRouter()


@router.post("", response_model=OptimizationResponse, status_code=200)
def record_optimization(payload: OptimizationRequest):
    tokens_saved = payload.baseline_tokens - payload.optimized_tokens
    improvement_pct = round(tokens_saved / payload.baseline_tokens * 100, 2)
    recorded_at = datetime.now(timezone.utc).isoformat()

    with get_conn() as conn:
        conn.execute(
            """INSERT INTO optimizations
               (user_id, baseline_tokens, optimized_tokens,
                improvement_pct, tokens_saved, recorded_at)
               VALUES (?,?,?,?,?,?)""",
            (payload.user_id, payload.baseline_tokens, payload.optimized_tokens,
             improvement_pct, tokens_saved, recorded_at),
        )

    # Reflect savings in score by injecting a synthetic event for saved tokens
    # (we record the optimized cost as the new event)
    update_user_score(payload.user_id)

    return OptimizationResponse(
        user_id=payload.user_id,
        baseline_tokens=payload.baseline_tokens,
        optimized_tokens=payload.optimized_tokens,
        improvement_pct=improvement_pct,
        tokens_saved=tokens_saved,
        recorded_at=recorded_at,
    )


@router.get("/{user_id}", response_model=list[OptimizationResponse])
def get_optimizations(user_id: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM optimizations WHERE user_id = ? ORDER BY recorded_at DESC",
            (user_id,),
        ).fetchall()
    return [OptimizationResponse(**dict(r)) for r in rows]
