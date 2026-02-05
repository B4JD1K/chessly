"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createBotGame, BotDifficulty, BOT_DIFFICULTY_LABELS } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Loader2, Bot, User } from "lucide-react";

const DIFFICULTIES: BotDifficulty[] = ["beginner", "easy", "medium", "hard", "expert", "master"];

export default function PlayBotPage() {
  const router = useRouter();
  const { session, discordId } = useUser();
  const [selectedDifficulty, setSelectedDifficulty] = useState<BotDifficulty>("medium");
  const [selectedColor, setSelectedColor] = useState<"white" | "black" | "random">("white");
  const [isCreating, setIsCreating] = useState(false);

  const handleStartGame = async () => {
    if (!discordId) return;

    setIsCreating(true);
    try {
      // Resolve random color before creating game
      const actualColor = selectedColor === "random"
        ? (Math.random() < 0.5 ? "white" : "black")
        : selectedColor;
      const game = await createBotGame(discordId, selectedDifficulty, actualColor);
      router.push(`/play/bot/${game.id}`);
    } catch (error) {
      console.error("Failed to create game:", error);
      setIsCreating(false);
    }
  };

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-12">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Play vs Bot</CardTitle>
            <CardDescription>
              Play against Stockfish chess engine
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={() => router.push("/login")} className="w-full">
              Login to Play
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
              onClick={() => router.push("/play/bot/anonymous")}
              className="w-full"
            >
              <User className="h-4 w-4 mr-2" />
              Play as Guest
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Guest games run in your browser and won&apos;t be saved.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-lg mx-auto">
        <h1 className="text-3xl font-bold text-center mb-2">Play vs Bot</h1>
        <p className="text-center text-muted-foreground mb-8">
          <Bot className="inline-block w-5 h-5 mr-1" />
          Powered by Stockfish
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Game Settings</CardTitle>
            <CardDescription>
              Choose difficulty and color
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Difficulty selection */}
            <div>
              <label className="text-sm font-medium mb-3 block">
                Difficulty
              </label>
              <div className="grid grid-cols-2 gap-2">
                {DIFFICULTIES.map((diff) => (
                  <Button
                    key={diff}
                    variant={selectedDifficulty === diff ? "default" : "outline"}
                    onClick={() => setSelectedDifficulty(diff)}
                    className="w-full justify-between"
                  >
                    <span>{BOT_DIFFICULTY_LABELS[diff].name}</span>
                    <span className="text-xs opacity-70">
                      ~{BOT_DIFFICULTY_LABELS[diff].elo}
                    </span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Color selection */}
            <div>
              <label className="text-sm font-medium mb-3 block">
                Play as
              </label>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  variant={selectedColor === "white" ? "default" : "outline"}
                  onClick={() => setSelectedColor("white")}
                  className="w-full"
                >
                  <span className="text-2xl mr-2">♔</span>
                  White
                </Button>
                <Button
                  variant={selectedColor === "random" ? "default" : "outline"}
                  onClick={() => setSelectedColor("random")}
                  className="w-full"
                >
                  <span className="text-2xl mr-2">?</span>
                  Random
                </Button>
                <Button
                  variant={selectedColor === "black" ? "default" : "outline"}
                  onClick={() => setSelectedColor("black")}
                  className="w-full"
                >
                  <span className="text-2xl mr-2">♚</span>
                  Black
                </Button>
              </div>
            </div>

            <Button
              onClick={handleStartGame}
              disabled={isCreating}
              className="w-full"
              size="lg"
            >
              {isCreating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                "Start Game"
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
