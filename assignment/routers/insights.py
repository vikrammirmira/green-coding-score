from fastapi import APIRouter, HTTPException
from database import get_conn
from registration.models.schemas import InsightsResponse
from models.services.calculator import ENERGY_PER_TOKEN_KWH, CARBON_INTENSITY_GCO2_PER_KWH

router = APIRouter()


@router.get("/{user_id}", response_model=InsightsResponse)
def get_insights(user_id: str):
    with get_conn() as conn:
        row = conn.execute(
            """SELECT
                 COUNT(*)              AS optimization_count,
                 SUM(tokens_saved)     AS total_tokens_saved,
                 MAX(improvement_pct)  AS best_improvement_pct
               FROM optimizations WHERE user_id = ?""",
            (user_id,),
        ).fetchone()

    total_tokens_saved = row["total_tokens_saved"] or 0
    total_carbon_saved = (
        total_tokens_saved * ENERGY_PER_TOKEN_KWH * CARBON_INTENSITY_GCO2_PER_KWH
    )

    return InsightsResponse(
        user_id=user_id,
        total_tokens_saved=total_tokens_saved,
        total_carbon_saved_gco2=round(total_carbon_saved, 6),
        best_improvement_pct=row["best_improvement_pct"],
        optimization_count=row["optimization_count"] or 0,
    )
