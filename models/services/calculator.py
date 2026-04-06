"""
Final scoring model for Green Coding Score.

Goals:
- Avoid saturation at 100
- Provide meaningful differentiation
- Keep scoring interpretable
"""

import os
import math

# ── Config ─────────────────────────────────────────────────────────────────────

ENERGY_PER_TOKEN_KWH: float = float(os.environ.get("ENERGY_PER_TOKEN_KWH", "0.000001"))
CARBON_INTENSITY_GCO2_PER_KWH: float = float(os.environ.get("CARBON_INTENSITY_GCO2_PER_KWH", "475.0"))

EFFICIENCY_WEIGHT: float = float(os.environ.get("EFFICIENCY_WEIGHT", "0.6"))
CARBON_WEIGHT: float = float(os.environ.get("CARBON_WEIGHT", "0.4"))

BASELINE_TOKENS_PER_EVENT: int = int(os.environ.get("BASELINE_TOKENS_PER_EVENT", "100"))

# Controls how aggressively large prompts are penalized
VERBOSITY_THRESHOLD: int = int(os.environ.get("VERBOSITY_THRESHOLD", "120"))

BADGE_RULES = [
    (90.0, "Low Carbon Champion"),
    (80.0, "Efficient Coder"),
    (50.0, "Green Starter"),
]


# ── Core Calculations ──────────────────────────────────────────────────────────

def calc_energy(total_tokens: int) -> float:
    return total_tokens * ENERGY_PER_TOKEN_KWH


def calc_carbon(energy_kwh: float) -> float:
    return energy_kwh * CARBON_INTENSITY_GCO2_PER_KWH


# ── Scoring Functions ──────────────────────────────────────────────────────────

def calc_efficiency_score(avg_tokens_per_event: float) -> float:
    if avg_tokens_per_event <= 0:
        return 100.0

    # Normalize relative to baseline
    ratio = avg_tokens_per_event / BASELINE_TOKENS_PER_EVENT

    # Stronger penalty using power curve
    score = 100 * (1 / (1 + (ratio * 5)))

    return round(min(max(score, 0.0), 100.0), 2)


def calc_carbon_score(total_carbon_gco2: float, event_count: int) -> float:
    """
    Carbon score based on per-event emissions.

    Lower carbon per event → higher score.
    """
    if event_count == 0:
        return 100.0

    avg_carbon = total_carbon_gco2 / event_count

    # Define a reasonable carbon threshold per request
    CARBON_BASELINE = calc_carbon(calc_energy(BASELINE_TOKENS_PER_EVENT))

    ratio = CARBON_BASELINE / (avg_carbon + 1e-6)

    normalized = math.log1p(ratio) / math.log1p(CARBON_BASELINE + 1)

    score = normalized * 100

    return round(min(max(score, 0.0), 100.0), 2)


def calc_total_score(efficiency_score: float, carbon_score: float) -> float:
    score = (
            EFFICIENCY_WEIGHT * efficiency_score +
            CARBON_WEIGHT * carbon_score
    )
    return round(min(max(score, 0.0), 100.0), 2)


def evaluate_badges(total_score: float) -> list[str]:
    return [badge for threshold, badge in BADGE_RULES if total_score >= threshold]