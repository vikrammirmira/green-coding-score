import time
from fastapi import APIRouter, Query
from database import get_conn
from registration.models.schemas import LeaderboardResponse, LeaderboardEntry

router = APIRouter()

# Simple in-process cache
_cache: dict = {"data": None, "expires_at": 0.0}
CACHE_TTL_SECONDS = 30


@router.get("", response_model=LeaderboardResponse)
def get_leaderboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    now = time.time()

    # Refresh cache if stale
    if _cache["data"] is None or now > _cache["expires_at"]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT user_id, total_score, total_tokens, total_carbon_gco2 "
                "FROM scores ORDER BY total_score DESC"
            ).fetchall()
        _cache["data"] = [dict(r) for r in rows]
        _cache["expires_at"] = now + CACHE_TTL_SECONDS

    all_entries = _cache["data"]
    total = len(all_entries)
    start = (page - 1) * page_size
    page_entries = all_entries[start: start + page_size]

    entries = [
        LeaderboardEntry(rank=start + i + 1, **e)
        for i, e in enumerate(page_entries)
    ]

    return LeaderboardResponse(
        entries=entries,
        total=total,
        page=page,
        page_size=page_size,
    )
