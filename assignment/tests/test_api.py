"""
Tests for the Green Coding Score API.
Run with: pytest tests/ -v
"""

import os
import pytest
from fastapi.testclient import TestClient

# Use an isolated in-memory DB for tests
os.environ["DB_PATH"] = ":memory:"

from app.main import app
from app.database import init_db

init_db()

client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────────────────

def post_event(user_id="alice", input_tokens=1000, output_tokens=500, model="gpt-4"):
    return client.post("/events/llm", json={
        "user_id": user_id,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model": model,
    })


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── Event Ingestion ────────────────────────────────────────────────────────────

def test_ingest_valid_event():
    r = post_event("user_ingest_1")
    assert r.status_code == 200
    data = r.json()
    assert "event_id" in data
    assert data["total_tokens"] == 1500
    assert data["energy_kwh"] > 0
    assert data["carbon_gco2"] > 0
    assert data["user_id"] == "user_ingest_1"


def test_ingest_zero_tokens():
    r = post_event("user_zero", input_tokens=0, output_tokens=0)
    assert r.status_code == 200
    assert r.json()["total_tokens"] == 0


def test_ingest_invalid_payload():
    r = client.post("/events/llm", json={"user_id": "x"})  # missing required fields
    assert r.status_code == 422


def test_ingest_negative_tokens():
    r = client.post("/events/llm", json={
        "user_id": "x", "input_tokens": -1, "output_tokens": 0, "model": "gpt-4"
    })
    assert r.status_code == 422


# ── Score ──────────────────────────────────────────────────────────────────────

def test_score_created_after_event():
    post_event("user_score_1")
    r = client.get("/score/user_score_1")
    assert r.status_code == 200
    data = r.json()
    assert 0 <= data["total_score"] <= 100
    assert data["event_count"] == 1


def test_score_not_found():
    r = client.get("/score/nonexistent_user_xyz")
    assert r.status_code == 404


def test_score_updates_with_multiple_events():
    post_event("user_multi", input_tokens=500, output_tokens=0)
    post_event("user_multi", input_tokens=500, output_tokens=0)
    r = client.get("/score/user_multi")
    assert r.json()["event_count"] == 2
    assert r.json()["total_tokens"] == 1000


def test_score_range_normalized():
    post_event("user_norm", input_tokens=100, output_tokens=50)
    r = client.get("/score/user_norm")
    score = r.json()["total_score"]
    assert 0 <= score <= 100


# ── Energy & Carbon calculation ────────────────────────────────────────────────

def test_energy_carbon_values():
    from app.services.calculator import calc_energy, calc_carbon, ENERGY_PER_TOKEN_KWH, CARBON_INTENSITY_GCO2_PER_KWH
    energy = calc_energy(1000)
    assert energy == pytest.approx(1000 * ENERGY_PER_TOKEN_KWH)
    carbon = calc_carbon(energy)
    assert carbon == pytest.approx(energy * CARBON_INTENSITY_GCO2_PER_KWH)


def test_efficiency_score_low_usage():
    from app.services.calculator import calc_efficiency_score
    # Far below baseline → score should be high
    score = calc_efficiency_score(100)
    assert score > 80


def test_efficiency_score_high_usage():
    from app.services.calculator import calc_efficiency_score
    # Far above baseline → score should be low
    score = calc_efficiency_score(100_000)
    assert score < 10


# ── Leaderboard ────────────────────────────────────────────────────────────────

def test_leaderboard_returns_entries():
    post_event("lb_user_a")
    post_event("lb_user_b", input_tokens=200, output_tokens=0)
    r = client.get("/leaderboard")
    assert r.status_code == 200
    data = r.json()
    assert "entries" in data
    assert data["total"] >= 2


def test_leaderboard_pagination():
    r = client.get("/leaderboard?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["entries"]) <= 2
    assert data["page"] == 1


def test_leaderboard_sorted_desc():
    r = client.get("/leaderboard?page_size=100")
    entries = r.json()["entries"]
    scores = [e["total_score"] for e in entries]
    assert scores == sorted(scores, reverse=True)


# ── Badges ─────────────────────────────────────────────────────────────────────

def test_badges_empty_for_new_user():
    post_event("badge_user_new", input_tokens=50000, output_tokens=50000)
    r = client.get("/badges/badge_user_new")
    assert r.status_code == 200
    # High token usage → low score → no badges


def test_badge_awarded_for_efficient_user():
    # Very efficient user — minimal tokens
    for _ in range(3):
        post_event("badge_champ", input_tokens=10, output_tokens=5)
    r = client.get("/badges/badge_champ")
    assert r.status_code == 200
    # Efficient users should earn at least the Green Starter badge
    assert isinstance(r.json()["badges"], list)


def test_no_duplicate_badges():
    post_event("badge_dedup", input_tokens=10, output_tokens=5)
    post_event("badge_dedup", input_tokens=10, output_tokens=5)
    r = client.get("/badges/badge_dedup")
    badges = r.json()["badges"]
    assert len(badges) == len(set(badges))


# ── Optimizations ─────────────────────────────────────────────────────────────

def test_record_optimization():
    r = client.post("/optimizations", json={
        "user_id": "opt_user_1",
        "baseline_tokens": 2000,
        "optimized_tokens": 1200,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["tokens_saved"] == 800
    assert data["improvement_pct"] == pytest.approx(40.0)


def test_optimization_invalid_if_optimized_gte_baseline():
    r = client.post("/optimizations", json={
        "user_id": "opt_user_2",
        "baseline_tokens": 1000,
        "optimized_tokens": 1000,
    })
    assert r.status_code == 422


def test_get_optimizations_list():
    client.post("/optimizations", json={
        "user_id": "opt_list_user",
        "baseline_tokens": 3000,
        "optimized_tokens": 1500,
    })
    r = client.get("/optimizations/opt_list_user")
    assert r.status_code == 200
    assert len(r.json()) >= 1


# ── Insights ──────────────────────────────────────────────────────────────────

def test_insights_no_optimizations():
    post_event("insights_blank")
    r = client.get("/insights/insights_blank")
    assert r.status_code == 200
    data = r.json()
    assert data["total_tokens_saved"] == 0
    assert data["optimization_count"] == 0


def test_insights_with_optimizations():
    client.post("/optimizations", json={
        "user_id": "insights_user",
        "baseline_tokens": 2000,
        "optimized_tokens": 800,
    })
    client.post("/optimizations", json={
        "user_id": "insights_user",
        "baseline_tokens": 1000,
        "optimized_tokens": 400,
    })
    r = client.get("/insights/insights_user")
    data = r.json()
    assert data["total_tokens_saved"] == 1800
    assert data["optimization_count"] == 2
    assert data["best_improvement_pct"] == pytest.approx(60.0)
    assert data["total_carbon_saved_gco2"] > 0
