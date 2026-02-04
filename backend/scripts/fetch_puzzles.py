#!/usr/bin/env python3
"""
Script to fetch daily puzzles from multiple sources and add them to the database.

Sources:
- Lichess (lichess.org)
- Chess.com (chess.com)

Usage:
    # Fetch puzzles for tomorrow
    python scripts/fetch_puzzles.py

    # Fetch puzzles for next 7 days
    python scripts/fetch_puzzles.py --days 7

    # Fetch puzzle for specific date
    python scripts/fetch_puzzles.py --date 2026-02-10

Environment:
    DATABASE_URL - PostgreSQL connection string
"""

import os
import sys
import argparse
from datetime import date, timedelta

import requests
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.puzzle import Puzzle


# API endpoints
LICHESS_DAILY_API = "https://lichess.org/api/puzzle/daily"
CHESSCOM_DAILY_API = "https://api.chess.com/pub/puzzle"


def get_database_url():
    """Get database URL from environment."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    return url


def fetch_lichess_puzzle():
    """Fetch daily puzzle from Lichess."""
    try:
        response = requests.get(LICHESS_DAILY_API, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Lichess puzzle format
            game = data.get("game", {})
            puzzle = data.get("puzzle", {})

            # The FEN in Lichess is the position BEFORE the first move
            # The solution starts with opponent's move, then player moves
            fen = game.get("fen", "")
            solution = puzzle.get("solution", [])

            # For our format, we need the position after opponent's first move
            # and solution without that first move
            if solution:
                # Apply first move to get starting position for player
                import chess
                board = chess.Board(fen)
                first_move = chess.Move.from_uci(solution[0])
                board.push(first_move)

                return {
                    "fen": board.fen(),
                    "solution": " ".join(solution[1:]),  # Skip opponent's first move
                    "rating": puzzle.get("rating", 1500),
                    "themes": " ".join(puzzle.get("themes", [])),
                    "source": "lichess",
                }
        print(f"Lichess API returned status {response.status_code}")
    except Exception as e:
        print(f"Error fetching from Lichess: {e}")
    return None


def fetch_chesscom_puzzle():
    """Fetch daily puzzle from Chess.com."""
    try:
        response = requests.get(CHESSCOM_DAILY_API, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Chess.com puzzle format
            fen = data.get("fen", "")

            # Chess.com provides PGN, we need to extract solution
            pgn = data.get("pgn", "")

            # Parse PGN to get moves - this is simplified
            # Chess.com format varies, so we'll use a basic approach
            import chess
            import chess.pgn
            import io

            try:
                game = chess.pgn.read_game(io.StringIO(pgn))
                if game:
                    board = game.board()
                    moves = []
                    for move in game.mainline_moves():
                        moves.append(move.uci())
                        board.push(move)

                    if moves:
                        return {
                            "fen": fen,
                            "solution": " ".join(moves),
                            "rating": 1500,  # Chess.com doesn't always provide rating
                            "themes": "tactics",
                            "source": "chess.com",
                        }
            except Exception as pgn_error:
                print(f"Error parsing Chess.com PGN: {pgn_error}")

        print(f"Chess.com API returned status {response.status_code}")
    except Exception as e:
        print(f"Error fetching from Chess.com: {e}")
    return None


def add_puzzle_to_db(session, puzzle_data: dict, puzzle_date: date) -> bool:
    """Add puzzle to database for specific date."""
    # Check if puzzle from this source already exists for this date
    existing = session.query(Puzzle).filter(
        and_(
            Puzzle.daily_date == puzzle_date,
            Puzzle.source == puzzle_data["source"]
        )
    ).first()

    if existing:
        print(f"Puzzle from {puzzle_data['source']} already exists for {puzzle_date}")
        return False

    puzzle = Puzzle(
        fen=puzzle_data["fen"],
        solution=puzzle_data["solution"],
        rating=puzzle_data["rating"],
        themes=puzzle_data["themes"],
        source=puzzle_data["source"],
        daily_date=puzzle_date,
    )
    session.add(puzzle)
    session.commit()
    print(f"Added {puzzle_data['source']} puzzle for {puzzle_date} (rating: {puzzle_data['rating']})")
    return True


def fetch_all_puzzles(session, target_date: date):
    """Fetch puzzles from all sources for a given date."""
    sources = [
        ("Lichess", fetch_lichess_puzzle),
        ("Chess.com", fetch_chesscom_puzzle),
    ]

    added = 0
    for name, fetch_func in sources:
        print(f"Fetching from {name}...")
        puzzle_data = fetch_func()
        if puzzle_data:
            if add_puzzle_to_db(session, puzzle_data, target_date):
                added += 1
        else:
            print(f"  Failed to fetch from {name}")

    return added


def main():
    parser = argparse.ArgumentParser(description="Fetch puzzles from multiple sources")
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to fetch puzzles for (default: 1)"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to fetch puzzles for (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    # Setup database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if args.date:
            # Fetch for specific date
            target_date = date.fromisoformat(args.date)
            fetch_all_puzzles(session, target_date)
        else:
            # Fetch for next N days starting from tomorrow
            start_date = date.today() + timedelta(days=1)
            for i in range(args.days):
                target_date = start_date + timedelta(days=i)
                print(f"\n=== Fetching puzzles for {target_date} ===")
                fetch_all_puzzles(session, target_date)
    finally:
        session.close()


if __name__ == "__main__":
    main()
