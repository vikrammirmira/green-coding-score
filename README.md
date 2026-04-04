# Green Coding Score API

Track compute usage, estimate energy & carbon impact, and gamify sustainable engineering.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

## Run Tests

```bash
pytest tests/ -v
```

---

## API Reference

### POST /events/llm
Ingest an LLM usage event.

**Request:**
```json
{
  "user_id": "alice",
  "input_tokens": 1000,
  "output_tokens": 500,
  "model": "gpt-4"
}
```

**Response:**
```json
{
  "event_id": "uuid",
  "user_id": "alice",
  "total_tokens": 1500,
  "energy_kwh": 0.0015,
  "carbon_gco2": 0.7125,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### GET /score/{user_id}
Get the current Green Coding Score for a user.

**Response:**
```json
{
  "user_id": "alice",
  "total_score": 87.5,
  "efficiency_score": 90.0,
  "carbon_score": 85.0,
  "total_tokens": 4500,
  "total_energy_kwh": 0.0045,
  "total_carbon_gco2": 2.1375,
  "event_count": 3,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### GET /leaderboard?page=1&page_size=10
Get paginated leaderboard sorted by score descending.

---

### GET /badges/{user_id}
Get badges earned by a user.

**Badge Rules:**
| Badge | Threshold |
|---|---|
| Green Starter | Score ≥ 50 |
| Efficient Coder | Score ≥ 80 |
| Low Carbon Champion | Score ≥ 90 |

---

### POST /optimizations
Record a before/after token optimization.

**Request:**
```json
{
  "user_id": "alice",
  "baseline_tokens": 2000,
  "optimized_tokens": 1200
}
```

---

### GET /optimizations/{user_id}
List all optimizations for a user.

---

### GET /insights/{user_id}
Get aggregated sustainability insights.

**Response:**
```json
{
  "user_id": "alice",
  "total_tokens_saved": 800,
  "total_carbon_saved_gco2": 0.38,
  "best_improvement_pct": 40.0,
  "optimization_count": 1
}
```

---

## Configuration (Environment Variables)

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `green_coding.db` | SQLite file path |
| `ENERGY_PER_TOKEN_KWH` | `0.000001` | Energy factor per token |
| `CARBON_INTENSITY_GCO2_PER_KWH` | `475.0` | Region carbon intensity |
| `EFFICIENCY_WEIGHT` | `0.5` | Score weight for efficiency |
| `CARBON_WEIGHT` | `0.5` | Score weight for carbon |
| `BASELINE_TOKENS_PER_EVENT` | `2000` | Token baseline for scoring |

## Project Structure

```
green_coding_score/
├── app/
│   ├── main.py              # FastAPI app + router registration
│   ├── database.py          # SQLite setup + connection
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── services/
│   │   ├── calculator.py    # Energy, carbon, scoring, badge logic
│   │   └── score_service.py # Score recomputation + badge assignment
│   └── routers/
│       ├── events.py        # POST /events/llm
│       ├── scores.py        # GET /score/{user_id}
│       ├── leaderboard.py   # GET /leaderboard
│       ├── badges.py        # GET /badges/{user_id}
│       ├── optimizations.py # POST/GET /optimizations
│       └── insights.py      # GET /insights/{user_id}
├── tests/
│   └── test_api.py          # Full test suite (35 tests)
├── requirements.txt
└── README.md
```
