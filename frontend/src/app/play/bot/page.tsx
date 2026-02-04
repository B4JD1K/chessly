"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createBotGame, BotDifficulty, BOT_DIFFICULTY_LABELS } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Loader2, Bot } from "lucide-react";

const DIFFICULTIES: BotDifficulty[] = ["beginner", "easy", "medium", "hard", "expert", "master"];

export default function PlayBotPage() {
  const router = useRouter();
  const { session, discordId } = useUser();
  const [selectedDifficulty, setSelectedDifficulty] = useState<BotDifficulty>("medium");
  const [selectedColor, setSelectedColor] = useState<"white" | "black">("white");
  const [isCreating, setIsCreating] = useState(false);

  const handleStartGame = async () => {
    if (!discordId) return;

    setIsCreating(true);
    try {
      const game = await createBotGame(discordId, selectedDifficulty, selectedColor);
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
              Login with Discord to play against Stockfish
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push("/login")} className="w-full">
              Login to Play
            </Button>
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
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant={selectedColor === "white" ? "default" : "outline"}
                  onClick={() => setSelectedColor("white")}
                  className="w-full"
                >
                  <span className="text-2xl mr-2">♔</span>
                  White
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
