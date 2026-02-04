#!/usr/bin/env python3
"""
Script to fetch daily puzzles from Lichess API and add them to the database.

Usage:
    # Fetch puzzle for tomorrow
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
import random
from datetime import date, timedelta

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.puzzle import Puzzle


LICHESS_PUZZLE_API = "https://lichess.org/api/puzzle/daily"
LICHESS_RANDOM_PUZZLE_API = "https://lichess.org/api/puzzle/next"


def get_database_url():
    """Get database URL from environment."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    return url


def fetch_lichess_puzzle():
    """Fetch a random puzzle from Lichess."""
    # Use daily puzzle endpoint
    response = requests.get(LICHESS_PUZZLE_API)
    if response.status_code == 200:
        data = response.json()
        return {
            "fen": data["game"]["fen"],
            "solution": " ".join(data["puzzle"]["solution"]),
            "rating": data["puzzle"]["rating"],
            "themes": " ".join(data["puzzle"]["themes"]),
        }

    # Fallback: fetch from puzzle database CSV
    # Lichess provides puzzle database at https://database.lichess.org/
    print(f"Warning: Could not fetch from Lichess API (status {response.status_code})")
    return None


def fetch_random_puzzle_from_db():
    """Fetch a random puzzle from Lichess puzzle database."""
    # This uses the streaming API to get a random puzzle
    response = requests.get(
        "https://lichess.org/api/puzzle/next",
        headers={"Accept": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        return {
            "fen": data["game"]["fen"],
            "solution": " ".join(data["puzzle"]["solution"]),
            "rating": data["puzzle"]["rating"],
            "themes": " ".join(data["puzzle"]["themes"]),
        }
    return None


def add_puzzle_to_db(session, puzzle_data: dict, puzzle_date: date) -> bool:
    """Add puzzle to database for specific date."""
    # Check if puzzle already exists for this date
    existing = session.query(Puzzle).filter(Puzzle.daily_date == puzzle_date).first()
    if existing:
        print(f"Puzzle already exists for {puzzle_date}")
        return False

    puzzle = Puzzle(
        fen=puzzle_data["fen"],
        solution=puzzle_data["solution"],
        rating=puzzle_data["rating"],
        themes=puzzle_data["themes"],
        daily_date=puzzle_date,
    )
    session.add(puzzle)
    session.commit()
    print(f"Added puzzle for {puzzle_date} (rating: {puzzle_data['rating']})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Fetch puzzles from Lichess")
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to fetch puzzles for (default: 1)"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Specific date to fetch puzzle for (YYYY-MM-DD)"
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
            puzzle_data = fetch_lichess_puzzle() or fetch_random_puzzle_from_db()
            if puzzle_data:
                add_puzzle_to_db(session, puzzle_data, target_date)
            else:
                print("Failed to fetch puzzle from Lichess")
        else:
            # Fetch for next N days starting from tomorrow
            start_date = date.today() + timedelta(days=1)
            for i in range(args.days):
                target_date = start_date + timedelta(days=i)
                puzzle_data = fetch_lichess_puzzle() or fetch_random_puzzle_from_db()
                if puzzle_data:
                    add_puzzle_to_db(session, puzzle_data, target_date)
                else:
                    print(f"Failed to fetch puzzle for {target_date}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
