"use client";

import { useEffect, useState, useCallback } from "react";
import { PuzzleBoard } from "@/components/puzzle-board";
import { getDailyPuzzles, completePuzzle, PuzzleResponse } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Flame, Trophy, ChevronLeft, ChevronRight } from "lucide-react";
import { useUser } from "@/hooks/use-user";

const SOURCE_LABELS: Record<string, string> = {
  lichess: "Lichess",
  "chess.com": "Chess.com",
};

// Helper functions for anonymous puzzle tracking
function getLocalStorageKey(): string {
  const today = new Date().toISOString().split("T")[0];
  return `chessly_puzzles_${today}`;
}

function getCompletedPuzzlesFromStorage(): Set<number> {
  if (typeof window === "undefined") return new Set();
  try {
    const stored = localStorage.getItem(getLocalStorageKey());
    if (stored) {
      const ids = JSON.parse(stored) as number[];
      return new Set(ids);
    }
  } catch {
    // Ignore parse errors
  }
  return new Set();
}

function saveCompletedPuzzleToStorage(puzzleId: number): void {
  if (typeof window === "undefined") return;
  try {
    const key = getLocalStorageKey();
    const existing = getCompletedPuzzlesFromStorage();
    existing.add(puzzleId);
    localStorage.setItem(key, JSON.stringify(Array.from(existing)));
  } catch {
    // Ignore storage errors
  }
}

export default function DailyPuzzlePage() {
  const { discordId, streak, refreshStreak } = useUser();
  const [puzzles, setPuzzles] = useState<PuzzleResponse[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedPuzzles, setCompletedPuzzles] = useState<Set<number>>(new Set());

  const puzzle = puzzles[currentIndex] || null;

  useEffect(() => {
    async function fetchPuzzles() {
      try {
        const data = await getDailyPuzzles();
        setPuzzles(data);
      } catch (err) {
        setError("No puzzles available for today. Check back later!");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchPuzzles();
  }, []);

  // Check if puzzle was already solved today (logged in or anonymous)
  useEffect(() => {
    if (discordId && streak?.puzzle_solved_today) {
      // Logged in user with streak - mark first puzzle as completed
      if (puzzles.length > 0) {
        setCompletedPuzzles(new Set([puzzles[0].id]));
      }
    } else if (!discordId && puzzles.length > 0) {
      // Anonymous user - check localStorage
      const storedCompleted = getCompletedPuzzlesFromStorage();
      const puzzleIds = new Set(puzzles.map(p => p.id));
      // Only keep IDs that match current puzzles
      const validCompleted = new Set(
        Array.from(storedCompleted).filter(id => puzzleIds.has(id))
      );
      if (validCompleted.size > 0) {
        setCompletedPuzzles(validCompleted);
      }
    }
  }, [discordId, streak, puzzles]);

  const handleComplete = useCallback(async (success: boolean) => {
    if (success && puzzle) {
      if (discordId) {
        // Logged in user - save to backend
        try {
          await completePuzzle(discordId, puzzle.id, true);
          setCompletedPuzzles(prev => new Set([...Array.from(prev), puzzle.id]));
          refreshStreak();
        } catch (error) {
          console.error("Failed to record completion:", error);
        }
      } else {
        // Anonymous user - save to localStorage
        saveCompletedPuzzleToStorage(puzzle.id);
        setCompletedPuzzles(prev => new Set([...Array.from(prev), puzzle.id]));
      }
    }
  }, [discordId, puzzle, refreshStreak]);

  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const goToNext = () => {
    if (currentIndex < puzzles.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || puzzles.length === 0) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Daily Puzzle</CardTitle>
            <CardDescription>{error || "No puzzles available"}</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Puzzles are added daily. Come back tomorrow for a new challenge!
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isCurrentPuzzleCompleted = puzzle && completedPuzzles.has(puzzle.id);
  const allPuzzlesCompleted = puzzles.every(p => completedPuzzles.has(p.id));

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-lg mx-auto">
        <h1 className="text-2xl font-bold text-center mb-2">Daily Puzzle</h1>

        {puzzles.length > 1 && (
          <div className="flex items-center justify-center gap-4 mb-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={goToPrevious}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <div className="flex gap-2">
              {puzzles.map((p, index) => (
                <Button
                  key={p.id}
                  variant={index === currentIndex ? "default" : "outline"}
                  size="sm"
                  onClick={() => setCurrentIndex(index)}
                  className="relative"
                >
                  {SOURCE_LABELS[p.source || ""] || `Puzzle ${index + 1}`}
                  {completedPuzzles.has(p.id) && (
                    <span className="absolute -top-1 -right-1 h-3 w-3 bg-green-500 rounded-full" />
                  )}
                </Button>
              ))}
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={goToNext}
              disabled={currentIndex === puzzles.length - 1}
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        )}

        <p className="text-center text-muted-foreground mb-2">
          {puzzle?.player_color === "white" ? "White" : "Black"} to move
        </p>
        <p className="text-center text-sm text-muted-foreground mb-6">
          Rating: {puzzle?.rating}
        </p>

        {allPuzzlesCompleted && (
          <Card className="mb-6 bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center gap-4">
                <Trophy className="h-8 w-8 text-green-600" />
                <div>
                  <p className="font-semibold text-green-700 dark:text-green-300">
                    All puzzles solved!
                  </p>
                  {discordId ? (
                    <div className="flex items-center gap-1 text-orange-500">
                      <Flame className="h-4 w-4" />
                      <span className="text-sm">
                        Streak: {streak?.current_streak || 1} day
                        {(streak?.current_streak || 1) !== 1 ? "s" : ""}
                      </span>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Log in to track your streak!
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {isCurrentPuzzleCompleted && !allPuzzlesCompleted && (
          <Card className="mb-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
            <CardContent className="pt-6">
              <p className="text-center text-blue-700 dark:text-blue-300">
                Puzzle solved! Try the next one.
              </p>
            </CardContent>
          </Card>
        )}

        {puzzle && (
          <PuzzleBoard
            key={puzzle.id}
            puzzle={puzzle}
            onComplete={handleComplete}
          />
        )}
      </div>
    </div>
  );
}
