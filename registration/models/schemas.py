from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime


# ── Events ────────────────────────────────────────────────────────────────────

class LLMEventRequest(BaseModel):
    user_id: str
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    model: str


class LLMEventResponse(BaseModel):
    event_id: str
    user_id: str
    total_tokens: int
    energy_kwh: float
    carbon_gco2: float
    timestamp: str


# ── Scores ────────────────────────────────────────────────────────────────────

class ScoreResponse(BaseModel):
    user_id: str
    total_score: float
    efficiency_score: float
    carbon_score: float
    total_tokens: int
    total_energy_kwh: float
    total_carbon_gco2: float
    event_count: int
    updated_at: str


# ── Leaderboard ───────────────────────────────────────────────────────────────

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    total_score: float
    total_tokens: int
    total_carbon_gco2: float


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    total: int
    page: int
    page_size: int


# ── Badges ────────────────────────────────────────────────────────────────────

class BadgeResponse(BaseModel):
    user_id: str
    badges: list[str]


# ── Optimizations ─────────────────────────────────────────────────────────────

class OptimizationRequest(BaseModel):
    user_id: str
    baseline_tokens: int = Field(..., gt=0)
    optimized_tokens: int = Field(..., ge=0)

    @model_validator(mode="after")
    def check_optimized_less_than_baseline(self):
        if self.optimized_tokens >= self.baseline_tokens:
            raise ValueError("optimized_tokens must be less than baseline_tokens")
        return self


class OptimizationResponse(BaseModel):
    user_id: str
    baseline_tokens: int
    optimized_tokens: int
    improvement_pct: float
    tokens_saved: int
    recorded_at: str


# ── Insights ──────────────────────────────────────────────────────────────────

class InsightsResponse(BaseModel):
    user_id: str
    total_tokens_saved: int
    total_carbon_saved_gco2: float
    best_improvement_pct: Optional[float]
    optimization_count: int
