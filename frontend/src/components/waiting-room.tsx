"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { GameResponse, TIME_CONTROL_LABELS, getGameWebSocketUrl } from "@/lib/api";
import { Copy, Check, Loader2 } from "lucide-react";

interface WaitingRoomProps {
  game: GameResponse;
  onGameStart: () => void;
  discordId: string;
}

export function WaitingRoom({ game, onGameStart, discordId }: WaitingRoomProps) {
  const [copied, setCopied] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const gameUrl = typeof window !== "undefined"
    ? `${window.location.origin}/play/${game.code}`
    : "";

  const copyLink = useCallback(async () => {
    await navigator.clipboard.writeText(gameUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [gameUrl]);

  // Connect WebSocket to listen for opponent joining
  useEffect(() => {
    const wsUrl = getGameWebSocketUrl(game.code, discordId);
    const websocket = new WebSocket(wsUrl);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "player_joined" || data.type === "game_start") {
        onGameStart();
      }
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [game.code, discordId, onGameStart]);

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader className="text-center">
            <CardTitle>Waiting for Opponent</CardTitle>
            <CardDescription>
              Share this link with a friend to start the game
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={gameUrl}
                readOnly
                className="flex-1 px-3 py-2 text-sm border rounded-md bg-muted"
              />
              <Button
                variant="outline"
                size="icon"
                onClick={copyLink}
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>

            <div className="text-center space-y-2">
              <div className="flex items-center justify-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Waiting for opponent to join...</span>
              </div>

              <div className="text-sm text-muted-foreground">
                Time control: {TIME_CONTROL_LABELS[game.time_control]}
              </div>
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground text-center">
                You are playing as <strong>White</strong>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
