from datetime import datetime, timezone
from database import get_conn
from models.services.calculator import (
    calc_efficiency_score,
    calc_carbon_score,
    calc_total_score,
    evaluate_badges,
)


def update_user_score(user_id: str) -> None:
    """Recompute and persist the score for a user, then evaluate badges."""
    with get_conn() as conn:
        row = conn.execute(
            """SELECT
                 COUNT(*)        AS event_count,
                 SUM(total_tokens) AS total_tokens,
                 SUM(energy_kwh)   AS total_energy_kwh,
                 SUM(carbon_gco2)  AS total_carbon_gco2
               FROM events WHERE user_id = ?""",
            (user_id,),
        ).fetchone()

        event_count = row["event_count"] or 0
        total_tokens = row["total_tokens"] or 0
        total_energy = row["total_energy_kwh"] or 0.0
        total_carbon = row["total_carbon_gco2"] or 0.0

        avg_tokens = total_tokens / event_count if event_count else 0
        eff_score = calc_efficiency_score(avg_tokens)
        carb_score = calc_carbon_score(total_carbon, event_count)
        total_score = calc_total_score(eff_score, carb_score)
        updated_at = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """INSERT INTO scores
               (user_id, efficiency_score, carbon_score, total_score,
                total_tokens, total_energy_kwh, total_carbon_gco2, event_count, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET
                 efficiency_score  = excluded.efficiency_score,
                 carbon_score      = excluded.carbon_score,
                 total_score       = excluded.total_score,
                 total_tokens      = excluded.total_tokens,
                 total_energy_kwh  = excluded.total_energy_kwh,
                 total_carbon_gco2 = excluded.total_carbon_gco2,
                 event_count       = excluded.event_count,
                 updated_at        = excluded.updated_at""",
            (user_id, eff_score, carb_score, total_score,
             total_tokens, total_energy, total_carbon, event_count, updated_at),
        )

        # Evaluate and assign badges
        earned = evaluate_badges(total_score)
        for badge in earned:
            conn.execute(
                """INSERT OR IGNORE INTO badges (user_id, badge, awarded_at)
                   VALUES (?, ?, ?)""",
                (user_id, badge, updated_at),
            )
