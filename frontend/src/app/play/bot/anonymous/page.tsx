"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BotDifficulty, BOT_DIFFICULTY_LABELS } from "@/lib/api";
import { AnonymousBotGameBoard } from "@/components/anonymous-bot-game-board";
import { Bot, ArrowLeft, Loader2 } from "lucide-react";

const DIFFICULTIES: BotDifficulty[] = ["beginner", "easy", "medium", "hard", "expert", "master"];

function AnonymousBotPlayContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Get initial settings from URL params
  const initialDifficulty = (searchParams.get("difficulty") as BotDifficulty) || "medium";
  const initialColorParam = searchParams.get("color");
  const initialColor = initialColorParam === "random"
    ? (Math.random() < 0.5 ? "white" : "black")
    : (initialColorParam as "white" | "black") || "white";

  const [gameStarted, setGameStarted] = useState(
    searchParams.has("difficulty") && searchParams.has("color")
  );
  const [selectedDifficulty, setSelectedDifficulty] = useState<BotDifficulty>(initialDifficulty);
  const [selectedColor, setSelectedColor] = useState<"white" | "black" | "random">(
    initialColorParam as "white" | "black" | "random" || "white"
  );
  const [actualColor, setActualColor] = useState<"white" | "black">(initialColor);

  const handleStartGame = () => {
    // Resolve random color
    const resolvedColor = selectedColor === "random"
      ? (Math.random() < 0.5 ? "white" : "black")
      : selectedColor;
    setActualColor(resolvedColor);
    setGameStarted(true);

    // Update URL without navigation
    const params = new URLSearchParams();
    params.set("difficulty", selectedDifficulty);
    params.set("color", resolvedColor);
    window.history.replaceState({}, "", `?${params.toString()}`);
  };

  const handleNewGame = () => {
    setGameStarted(false);
    // Clear URL params
    window.history.replaceState({}, "", window.location.pathname);
  };

  if (gameStarted) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-lg mx-auto">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNewGame}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Change Settings
          </Button>

          <h1 className="text-2xl font-bold text-center mb-2">Play vs Bot</h1>
          <p className="text-center text-muted-foreground mb-6">
            <Bot className="inline-block w-4 h-4 mr-1" />
            Browser Stockfish (Guest Mode)
          </p>

          <AnonymousBotGameBoard
            difficulty={selectedDifficulty}
            playerColor={actualColor}
            onNewGame={handleNewGame}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-lg mx-auto">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/play/bot")}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <h1 className="text-3xl font-bold text-center mb-2">Play vs Bot</h1>
        <p className="text-center text-muted-foreground mb-8">
          <Bot className="inline-block w-5 h-5 mr-1" />
          Guest Mode - No login required
        </p>

        <Card>
          <CardHeader>
            <CardTitle>Game Settings</CardTitle>
            <CardDescription>Choose difficulty and color</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Difficulty selection */}
            <div>
              <label className="text-sm font-medium mb-3 block">Difficulty</label>
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
              <label className="text-sm font-medium mb-3 block">Play as</label>
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

            <Button onClick={handleStartGame} className="w-full" size="lg">
              Start Game
            </Button>

            <p className="text-xs text-muted-foreground text-center">
              Game runs entirely in your browser. No account needed, but games
              won&apos;t be saved.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function AnonymousBotPlayPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <AnonymousBotPlayContent />
    </Suspense>
  );
}
