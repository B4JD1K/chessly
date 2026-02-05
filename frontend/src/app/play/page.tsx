"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createGame, TimeControl, TIME_CONTROL_LABELS, ColorChoice } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Loader2, Users, Bot, User } from "lucide-react";

const TIME_CONTROLS: TimeControl[] = [
  "bullet_1",
  "bullet_2",
  "blitz_3",
  "blitz_5",
  "rapid_10",
  "rapid_15",
];

// Helper to get/set guest name from localStorage
function getGuestName(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("chessly_guest_name") || "";
}

function setGuestNameStorage(name: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("chessly_guest_name", name);
  }
}

export default function PlayPage() {
  const router = useRouter();
  const { session, discordId } = useUser();
  const [selectedTime, setSelectedTime] = useState<TimeControl>("blitz_5");
  const [selectedColor, setSelectedColor] = useState<ColorChoice>("white");
  const [isCreating, setIsCreating] = useState(false);
  const [guestName, setGuestName] = useState("");

  // Load guest name from localStorage on mount
  useEffect(() => {
    const stored = getGuestName();
    if (stored) {
      setGuestName(stored);
    }
  }, []);

  const handleCreateGame = async () => {
    setIsCreating(true);

    // Save guest name for next time
    if (!discordId && guestName) {
      setGuestNameStorage(guestName);
    }

    try {
      const game = await createGame(discordId || null, {
        timeControl: selectedTime,
        color: selectedColor,
        guestName: discordId ? undefined : (guestName || "Guest"),
      });
      // Store player color for the game page
      if (!discordId) {
        sessionStorage.setItem(`game_${game.code}_color`, selectedColor === "random"
          ? (game.white_player ? "white" : "black")
          : selectedColor
        );
        sessionStorage.setItem(`game_${game.code}_guest`, guestName || "Guest");
      }
      router.push(`/play/${game.code}`);
    } catch (error) {
      console.error("Failed to create game:", error);
      setIsCreating(false);
    }
  };

  // Common game creation UI
  const renderGameCreation = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          Play with Friend
        </CardTitle>
        <CardDescription>
          Create a game and share the link
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Guest name input for anonymous users */}
        {!discordId && (
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
        )}

        <div>
          <label className="text-sm font-medium mb-2 block">
            Time Control
          </label>
          <div className="grid grid-cols-2 gap-2">
            {TIME_CONTROLS.map((tc) => (
              <Button
                key={tc}
                variant={selectedTime === tc ? "default" : "outline"}
                onClick={() => setSelectedTime(tc)}
                size="sm"
                className="w-full"
              >
                {TIME_CONTROL_LABELS[tc]}
              </Button>
            ))}
          </div>
        </div>

        {/* Color selection */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            Play as
          </label>
          <div className="grid grid-cols-3 gap-2">
            <Button
              variant={selectedColor === "white" ? "default" : "outline"}
              onClick={() => setSelectedColor("white")}
              size="sm"
              className="w-full"
            >
              <span className="text-lg mr-1">♔</span>
              White
            </Button>
            <Button
              variant={selectedColor === "random" ? "default" : "outline"}
              onClick={() => setSelectedColor("random")}
              size="sm"
              className="w-full"
            >
              <span className="text-lg mr-1">?</span>
              Random
            </Button>
            <Button
              variant={selectedColor === "black" ? "default" : "outline"}
              onClick={() => setSelectedColor("black")}
              size="sm"
              className="w-full"
            >
              <span className="text-lg mr-1">♚</span>
              Black
            </Button>
          </div>
        </div>

        <Button
          onClick={handleCreateGame}
          disabled={isCreating}
          className="w-full"
        >
          {isCreating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating...
            </>
          ) : (
            "Create Game"
          )}
        </Button>
      </CardContent>
    </Card>
  );

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-8">Play Chess</h1>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Play as Guest */}
            {renderGameCreation()}

            {/* Play vs Bot */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  Play vs Bot
                </CardTitle>
                <CardDescription>
                  Challenge Stockfish at various levels
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Play against the Stockfish engine with adjustable difficulty
                  from beginner (~800 ELO) to master (~2800 ELO).
                </p>

                <Button asChild className="w-full">
                  <Link href="/play/bot/anonymous">
                    Play vs Stockfish
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Login prompt */}
          <Card className="mt-6">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Want to save your games?</p>
                  <p className="text-sm text-muted-foreground">
                    Log in to track statistics and game history.
                  </p>
                </div>
                <Button variant="outline" onClick={() => router.push("/login")}>
                  <User className="h-4 w-4 mr-2" />
                  Login
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Play Chess</h1>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Play vs Friend */}
          {renderGameCreation()}

          {/* Play vs Bot */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Play vs Bot
              </CardTitle>
              <CardDescription>
                Challenge Stockfish at various levels
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Play against the Stockfish engine with adjustable difficulty
                from beginner (~800 ELO) to master (~2800 ELO).
              </p>

              <Button asChild className="w-full">
                <Link href="/play/bot">
                  Play vs Stockfish
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
