from fastapi import APIRouter, HTTPException
from database import get_conn
from registration.models.schemas import BadgeResponse

router = APIRouter()


@router.get("/{user_id}", response_model=BadgeResponse)
def get_badges(user_id: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT badge FROM badges WHERE user_id = ? ORDER BY awarded_at",
            (user_id,),
        ).fetchall()

    return BadgeResponse(user_id=user_id, badges=[r["badge"] for r in rows])
