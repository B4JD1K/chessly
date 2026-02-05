"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { GameBoard } from "@/components/game-board";
import { WaitingRoom } from "@/components/waiting-room";
import { getGame, joinGame, GameResponse } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import Link from "next/link";

// Helper to get/set guest name from localStorage
function getStoredGuestName(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("chessly_guest_name") || "";
}

function setStoredGuestName(name: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("chessly_guest_name", name);
  }
}

export default function GamePage() {
  const params = useParams();
  const router = useRouter();
  const code = params.code as string;
  const { session, discordId } = useUser();

  const [game, setGame] = useState<GameResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playerColor, setPlayerColor] = useState<"white" | "black" | null>(null);
  const [guestName, setGuestName] = useState("");
  const [isJoining, setIsJoining] = useState(false);
  const [showJoinForm, setShowJoinForm] = useState(false);
  const hasJoined = useRef(false);

  // Load guest name from localStorage
  useEffect(() => {
    const stored = getStoredGuestName();
    if (stored) {
      setGuestName(stored);
    }
  }, []);

  // Load player color from sessionStorage for creator
  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedColor = sessionStorage.getItem(`game_${code}_color`);
      const storedGuest = sessionStorage.getItem(`game_${code}_guest`);
      if (storedColor && !discordId) {
        setPlayerColor(storedColor as "white" | "black");
        if (storedGuest) {
          setGuestName(storedGuest);
        }
      }
    }
  }, [code, discordId]);

  // Fetch game
  useEffect(() => {
    async function fetchGame() {
      try {
        const gameData = await getGame(code);
        setGame(gameData);

        // For logged-in users, determine color
        if (discordId && session) {
          const isWhite = gameData.white_player?.id &&
            gameData.white_player.username === session?.user?.name;
          const isBlack = gameData.black_player?.id &&
            gameData.black_player.username === session?.user?.name;

          if (isWhite) {
            setPlayerColor("white");
          } else if (isBlack) {
            setPlayerColor("black");
          } else if (gameData.status === "waiting" && !hasJoined.current) {
            // Auto-join for logged-in users
            try {
              const joined = await joinGame(code, discordId);
              setGame(joined);
              // Determine color based on which slot was filled
              if (!joined.white_player?.id || joined.white_player.username !== session?.user?.name) {
                setPlayerColor("black");
              } else {
                setPlayerColor("white");
              }
              hasJoined.current = true;
            } catch (e) {
              console.error("Failed to join:", e);
            }
          }
        } else if (!discordId) {
          // Anonymous user - check if they're the creator
          const storedColor = sessionStorage.getItem(`game_${code}_color`);
          if (storedColor) {
            setPlayerColor(storedColor as "white" | "black");
            hasJoined.current = true;
          } else if (gameData.status === "waiting") {
            // Show join form for anonymous users
            setShowJoinForm(true);
          }
        }
      } catch (err) {
        setError("Game not found");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchGame();
  }, [code, discordId, session]);

  const handleAnonymousJoin = async () => {
    if (!game || game.status !== "waiting") return;

    setIsJoining(true);
    setStoredGuestName(guestName || "Guest");

    try {
      const joined = await joinGame(code, null, guestName || "Guest");
      setGame(joined);

      // Determine which color we got (opposite of creator)
      // If white slot was already filled, we're black, and vice versa
      const color = joined.white_player && !joined.black_player ? "black" :
                    joined.black_player && !joined.white_player ? "white" :
                    "black"; // default fallback

      setPlayerColor(color);
      sessionStorage.setItem(`game_${code}_color`, color);
      sessionStorage.setItem(`game_${code}_guest`, guestName || "Guest");
      setShowJoinForm(false);
      hasJoined.current = true;
    } catch (e) {
      console.error("Failed to join:", e);
      setError("Failed to join game");
    } finally {
      setIsJoining(false);
    }
  };

  const handleGameUpdate = useCallback((updatedGame: Partial<GameResponse>) => {
    setGame((prev) => prev ? { ...prev, ...updatedGame } : null);
  }, []);

  const handleGameStart = useCallback(() => {
    // Refresh game data when opponent joins
    getGame(code).then(setGame).catch(console.error);
  }, [code]);

  // Show join form for anonymous users who aren't the creator
  if (showJoinForm && !playerColor) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Join Game</CardTitle>
            <CardDescription>
              Enter your name to join this game
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Your Name
              </label>
              <Input
                placeholder="Guest"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                maxLength={20}
              />
            </div>
            <Button
              onClick={handleAnonymousJoin}
              disabled={isJoining}
              className="w-full"
            >
              {isJoining ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Joining...
                </>
              ) : (
                "Join Game"
              )}
            </Button>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">Or</span>
              </div>
            </div>
            <Button
              variant="outline"
              onClick={() => router.push("/login")}
              className="w-full"
            >
              Login with Discord
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
        discordId={discordId || undefined}
        guestName={!discordId ? guestName : undefined}
        playerColor={playerColor || undefined}
      />
    );
  }

  // Game in progress or completed
  return (
    <GameBoard
      game={game}
      playerColor={playerColor}
      discordId={discordId || undefined}
      guestName={!discordId ? guestName : undefined}
      onGameUpdate={handleGameUpdate}
    />
  );
}
