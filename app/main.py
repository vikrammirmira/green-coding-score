from fastapi import FastAPI
# from app.database import init_db
from database import init_db
from assignment.routers import events, scores, leaderboard, badges, insights, optimizations
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="Green Coding Score API",
    description="Track compute usage, estimate carbon impact, and gamify sustainable engineering.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(scores.router, prefix="/score", tags=["Scores"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(badges.router, prefix="/badges", tags=["Badges"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(optimizations.router, prefix="/optimizations", tags=["Optimizations"])

@app.get("/health")
def health():
    return {"status": "ok"}
