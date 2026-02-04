from datetime import date
from pydantic import BaseModel


class PuzzleCreate(BaseModel):
    fen: str
    solution: str
    rating: int = 1500
    themes: str | None = None
    daily_date: date | None = None


class PuzzleResponse(BaseModel):
    id: int
    fen: str
    rating: int
    themes: list[str]
    player_color: str  # "white" or "black"
    source: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_puzzle(cls, puzzle) -> "PuzzleResponse":
        fen_parts = puzzle.fen.split()
        # Player color is whoever has the move in the FEN
        player_color = "white" if fen_parts[1] == "w" else "black"
        themes = puzzle.themes.split(",") if puzzle.themes else []
        return cls(
            id=puzzle.id,
            fen=puzzle.fen,
            rating=puzzle.rating,
            themes=themes,
            player_color=player_color,
            source=puzzle.source,
        )
