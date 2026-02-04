"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { BotGameBoard } from "@/components/bot-game-board";
import { getBotGame, BotGameResponse } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import Link from "next/link";

export default function BotGamePage() {
  const params = useParams();
  const router = useRouter();
  const gameId = parseInt(params.id as string);
  const { session, discordId } = useUser();

  const [game, setGame] = useState<BotGameResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchGame() {
      try {
        const data = await getBotGame(gameId);
        setGame(data);
      } catch (err) {
        setError("Game not found");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (gameId) {
      fetchGame();
    }
  }, [gameId]);

  const handleGameUpdate = useCallback((updates: Partial<BotGameResponse>) => {
    setGame((prev) => prev ? { ...prev, ...updates } : null);
  }, []);

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Bot Game</CardTitle>
            <CardDescription>
              Login with Discord to view this game
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/login">Login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !game) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Game Not Found</CardTitle>
            <CardDescription>{error || "This game doesn't exist"}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/play/bot">Start New Game</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-lg mx-auto">
        <BotGameBoard
          game={game}
          discordId={discordId!}
          onGameUpdate={handleGameUpdate}
        />

        {game.status === "completed" && (
          <div className="mt-6 text-center">
            <Button asChild>
              <Link href="/play/bot">Play Again</Link>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
