from fastapi import APIRouter, HTTPException
from database import get_conn
from registration.models.schemas import ScoreResponse

router = APIRouter()


@router.get("/{user_id}", response_model=ScoreResponse)
def get_score(user_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM scores WHERE user_id = ?", (user_id,)
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return ScoreResponse(**dict(row))
