"use client";

import { useEffect, useState, useCallback } from "react";
import { PuzzleBoard } from "@/components/puzzle-board";
import { getDailyPuzzle, completePuzzle, PuzzleResponse } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Flame, Trophy } from "lucide-react";
import { useUser } from "@/hooks/use-user";

export default function DailyPuzzlePage() {
  const { discordId, streak, refreshStreak } = useUser();
  const [puzzle, setPuzzle] = useState<PuzzleResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    async function fetchPuzzle() {
      try {
        const data = await getDailyPuzzle();
        setPuzzle(data);
      } catch (err) {
        setError("No puzzle available for today. Check back later!");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchPuzzle();
  }, []);

  // Check if puzzle was already solved today
  useEffect(() => {
    if (streak?.puzzle_solved_today) {
      setCompleted(true);
    }
  }, [streak]);

  const handleComplete = useCallback(async (success: boolean) => {
    if (success && discordId && puzzle) {
      try {
        await completePuzzle(discordId, puzzle.id, true);
        setCompleted(true);
        refreshStreak();
      } catch (error) {
        console.error("Failed to record completion:", error);
      }
    }
  }, [discordId, puzzle, refreshStreak]);

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !puzzle) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Daily Puzzle</CardTitle>
            <CardDescription>{error || "No puzzle available"}</CardDescription>
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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-lg mx-auto">
        <h1 className="text-2xl font-bold text-center mb-2">Daily Puzzle</h1>
        <p className="text-center text-muted-foreground mb-6">
          {puzzle.player_color === "white" ? "White" : "Black"} to move
        </p>

        {completed && (
          <Card className="mb-6 bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center gap-4">
                <Trophy className="h-8 w-8 text-green-600" />
                <div>
                  <p className="font-semibold text-green-700 dark:text-green-300">
                    Puzzle solved!
                  </p>
                  <div className="flex items-center gap-1 text-orange-500">
                    <Flame className="h-4 w-4" />
                    <span className="text-sm">
                      Streak: {streak?.current_streak || 1} day
                      {(streak?.current_streak || 1) !== 1 ? "s" : ""}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <PuzzleBoard puzzle={puzzle} onComplete={handleComplete} />
      </div>
    </div>
  );
}
