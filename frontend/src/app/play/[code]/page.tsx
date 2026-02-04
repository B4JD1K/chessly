"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import { GameBoard } from "@/components/game-board";
import { WaitingRoom } from "@/components/waiting-room";
import { getGame, joinGame, GameResponse } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import Link from "next/link";

export default function GamePage() {
  const params = useParams();
  const code = params.code as string;
  const { session, discordId } = useUser();

  const [game, setGame] = useState<GameResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playerColor, setPlayerColor] = useState<"white" | "black" | null>(null);
  const hasJoined = useRef(false);

  // Fetch game and join if needed
  useEffect(() => {
    if (!discordId || hasJoined.current) return;

    const userId = discordId; // Capture for closure

    async function fetchAndJoin() {
      try {
        // First try to get the game
        let gameData = await getGame(code);

        // Determine if we're already in the game
        const isWhite = gameData.white_player?.id &&
          gameData.white_player.username === session?.user?.name;
        const isBlack = gameData.black_player?.id &&
          gameData.black_player.username === session?.user?.name;

        if (isWhite) {
          setPlayerColor("white");
        } else if (isBlack) {
          setPlayerColor("black");
        } else if (gameData.status === "waiting") {
          // Try to join as black
          try {
            gameData = await joinGame(code, userId);
            setPlayerColor("black");
          } catch (e) {
            console.error("Failed to join:", e);
          }
        }

        setGame(gameData);
        hasJoined.current = true;
      } catch (err) {
        setError("Game not found");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchAndJoin();
  }, [code, discordId, session]);

  const handleGameUpdate = useCallback((updatedGame: Partial<GameResponse>) => {
    setGame((prev) => prev ? { ...prev, ...updatedGame } : null);
  }, []);

  const handleGameStart = useCallback(() => {
    // Refresh game data when opponent joins
    if (discordId) {
      getGame(code).then(setGame).catch(console.error);
    }
  }, [code, discordId]);

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Join Game</CardTitle>
            <CardDescription>
              Login with Discord to join this game
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/login">Login to Play</Link>
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
              <Link href="/play">Create New Game</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Waiting for opponent
  if (game.status === "waiting") {
    return (
      <WaitingRoom
        game={game}
        onGameStart={handleGameStart}
        discordId={discordId!}
      />
    );
  }

  // Game in progress or completed
  return (
    <GameBoard
      game={game}
      playerColor={playerColor}
      discordId={discordId!}
      onGameUpdate={handleGameUpdate}
    />
  );
}
