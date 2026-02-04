from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import puzzles, users, games, bot_games, auth, lessons, achievements
# Import services to ensure event handlers are registered
from app import services  # noqa: F401

app = FastAPI(
    title="Chessly API",
    description="Chess puzzle training and multiplayer chess application",
    version="0.7.0",
)

# Build CORS origins list
cors_origins = [
    "http://localhost:3000",
    "https://discord.com",
]
if settings.frontend_url and settings.frontend_url not in cors_origins:
    cors_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.discordsays\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(puzzles.router, prefix="/puzzles", tags=["puzzles"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(games.router, prefix="/games", tags=["games"])
app.include_router(bot_games.router, prefix="/bot-games", tags=["bot-games"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
app.include_router(achievements.router, prefix="/achievements", tags=["achievements"])


@app.get("/health")
def health_check():
    return {"status": "healthy"}
