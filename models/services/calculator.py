"""
Core calculation and scoring logic.

Config values are intentionally kept as module-level constants so they are
easy to override via environment variables or a future config file.
"""

import os

# ── Energy / Carbon factors ────────────────────────────────────────────────────
# kWh per token (very rough approximation; adjust per model/region)
ENERGY_PER_TOKEN_KWH: float = float(os.environ.get("ENERGY_PER_TOKEN_KWH", "0.000001"))

# gCO2 per kWh — defaults to global average ~475 g/kWh
CARBON_INTENSITY_GCO2_PER_KWH: float = float(
    os.environ.get("CARBON_INTENSITY_GCO2_PER_KWH", "475.0")
)

# ── Scoring weights ────────────────────────────────────────────────────────────
EFFICIENCY_WEIGHT: float = float(os.environ.get("EFFICIENCY_WEIGHT", "0.5"))
CARBON_WEIGHT: float = float(os.environ.get("CARBON_WEIGHT", "0.5"))

# Baseline token count used to normalise the efficiency score.
# A user whose average tokens/event == this value gets a score of 50.
BASELINE_TOKENS_PER_EVENT: int = int(
    os.environ.get("BASELINE_TOKENS_PER_EVENT", "2000")
)

# ── Badge thresholds ───────────────────────────────────────────────────────────
BADGE_RULES: list[tuple[float, str]] = [
    (90.0, "Low Carbon Champion"),
    (80.0, "Efficient Coder"),
    (50.0, "Green Starter"),
]


# ── Calculations ───────────────────────────────────────────────────────────────

def calc_energy(total_tokens: int) -> float:
    """Return energy in kWh."""
    return total_tokens * ENERGY_PER_TOKEN_KWH


def calc_carbon(energy_kwh: float) -> float:
    """Return carbon in gCO2."""
    return energy_kwh * CARBON_INTENSITY_GCO2_PER_KWH


def calc_efficiency_score(avg_tokens_per_event: float) -> float:
    """
    Lower token usage → higher efficiency score (0–100).
    Score = 100 × (BASELINE / avg), clamped to [0, 100].
    """
    if avg_tokens_per_event <= 0:
        return 100.0
    raw = 100.0 * BASELINE_TOKENS_PER_EVENT / avg_tokens_per_event
    return round(min(max(raw, 0.0), 100.0), 2)


def calc_carbon_score(total_carbon_gco2: float, event_count: int) -> float:
    """
    Lower carbon per event → higher carbon score (0–100).
    Uses the same ratio logic as efficiency against a carbon baseline.
    """
    if event_count == 0:
        return 100.0
    baseline_carbon = calc_carbon(calc_energy(BASELINE_TOKENS_PER_EVENT))
    avg_carbon = total_carbon_gco2 / event_count
    if avg_carbon <= 0:
        return 100.0
    raw = 100.0 * baseline_carbon / avg_carbon
    return round(min(max(raw, 0.0), 100.0), 2)


def calc_total_score(efficiency_score: float, carbon_score: float) -> float:
    score = EFFICIENCY_WEIGHT * efficiency_score + CARBON_WEIGHT * carbon_score
    return round(min(max(score, 0.0), 100.0), 2)


def evaluate_badges(total_score: float) -> list[str]:
    """Return all badge names the user qualifies for based on their score."""
    return [badge for threshold, badge in BADGE_RULES if total_score >= threshold]
