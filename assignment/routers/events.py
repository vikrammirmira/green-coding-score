import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from database import get_conn
from registration.models.schemas import LLMEventRequest, LLMEventResponse
from models.services.calculator import calc_energy, calc_carbon
from badgelogic.score_service import update_user_score

router = APIRouter()


@router.post("/llm", response_model=LLMEventResponse, status_code=200)
def ingest_llm_event(payload: LLMEventRequest):
    event_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    total_tokens = payload.input_tokens + payload.output_tokens
    energy_kwh = calc_energy(total_tokens)
    carbon_gco2 = calc_carbon(energy_kwh)

    with get_conn() as conn:
        # Idempotency: if somehow the same UUID lands twice, ignore
        existing = conn.execute(
            "SELECT event_id FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Duplicate event")

        conn.execute(
            """INSERT INTO events
               (event_id, user_id, model, input_tokens, output_tokens,
                total_tokens, energy_kwh, carbon_gco2, timestamp)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (event_id, payload.user_id, payload.model,
             payload.input_tokens, payload.output_tokens,
             total_tokens, energy_kwh, carbon_gco2, timestamp),
        )

    update_user_score(payload.user_id)

    return LLMEventResponse(
        event_id=event_id,
        user_id=payload.user_id,
        total_tokens=total_tokens,
        energy_kwh=energy_kwh,
        carbon_gco2=carbon_gco2,
        timestamp=timestamp,
    )
