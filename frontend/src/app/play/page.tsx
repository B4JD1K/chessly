"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createGame, TimeControl, TIME_CONTROL_LABELS } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import { Loader2, Users, Bot } from "lucide-react";

const TIME_CONTROLS: TimeControl[] = [
  "bullet_1",
  "bullet_2",
  "blitz_3",
  "blitz_5",
  "rapid_10",
  "rapid_15",
];

export default function PlayPage() {
  const router = useRouter();
  const { session, discordId } = useUser();
  const [selectedTime, setSelectedTime] = useState<TimeControl>("blitz_5");
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateGame = async () => {
    if (!discordId) return;

    setIsCreating(true);
    try {
      const game = await createGame(discordId, selectedTime);
      router.push(`/play/${game.code}`);
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
            <CardTitle>Play Chess</CardTitle>
            <CardDescription>
              Login with Discord to play
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
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Play Chess</h1>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Play vs Friend */}
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
