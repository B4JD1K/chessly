from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import puzzles, users, games, bot_games, auth, lessons, achievements

app = FastAPI(
    title="Chessly API",
    description="Chess puzzle training and multiplayer chess application",
    version="0.7.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://discord.com",
        "https://*.discordsays.com",
    ],
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
