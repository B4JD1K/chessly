"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Chessboard } from "react-chessboard";
import { Chess, Square } from "chess.js";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ChessClock } from "@/components/chess-clock";
import {
  GameResponse,
  GameResult,
  getGameWebSocketUrl,
  TIME_CONTROL_LABELS,
} from "@/lib/api";
import { Flag, RotateCcw } from "lucide-react";

interface GameBoardProps {
  game: GameResponse;
  playerColor: "white" | "black" | null;
  discordId?: string;
  guestName?: string;
  onGameUpdate: (game: Partial<GameResponse>) => void;
}

export function GameBoard({
  game,
  playerColor,
  discordId,
  guestName,
  onGameUpdate,
}: GameBoardProps) {
  const [position, setPosition] = useState(game.current_fen);
  const [gameInstance] = useState(() => new Chess(game.current_fen));
  const [whiteTime, setWhiteTime] = useState(game.white_time_remaining);
  const [blackTime, setBlackTime] = useState(game.black_time_remaining);
  const [isWhiteTurn, setIsWhiteTurn] = useState(game.is_white_turn);
  const [gameOver, setGameOver] = useState(game.status === "completed");
  const [result, setResult] = useState<GameResult | null>(game.result);
  const [lastMoveTime, setLastMoveTime] = useState(Date.now());

  const wsRef = useRef<WebSocket | null>(null);
  const isSpectator = playerColor === null;
  const isMyTurn = !isSpectator && (
    (playerColor === "white" && isWhiteTurn) ||
    (playerColor === "black" && !isWhiteTurn)
  );

  // Connect WebSocket
  useEffect(() => {
    const wsUrl = getGameWebSocketUrl(game.code, {
      discordId,
      guestName,
      playerColor: playerColor || undefined,
    });
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "move") {
        gameInstance.load(data.fen);
        setPosition(data.fen);
        setWhiteTime(data.white_time);
        setBlackTime(data.black_time);
        setIsWhiteTurn(data.is_white_turn);
        setLastMoveTime(Date.now());
      } else if (data.type === "game_over") {
        setGameOver(true);
        setResult(data.result);
        onGameUpdate({ status: "completed", result: data.result });
      } else if (data.type === "player_disconnected") {
        console.log("Opponent disconnected");
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [game.code, discordId, guestName, playerColor, gameInstance, onGameUpdate]);

  const sendMove = useCallback((move: string, timeSpent: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "move",
        move,
        time_spent: timeSpent,
      }));
    }
  }, []);

  const handleResign = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && !gameOver) {
      wsRef.current.send(JSON.stringify({ type: "resign" }));
    }
  }, [gameOver]);

  const handleTimeout = useCallback((color: "white" | "black") => {
    if (wsRef.current?.readyState === WebSocket.OPEN && !gameOver) {
      wsRef.current.send(JSON.stringify({ type: "timeout", color }));
    }
  }, [gameOver]);

  const onDrop = useCallback(
    (sourceSquare: Square, targetSquare: Square, piece: string) => {
      if (gameOver || !isMyTurn) return false;

      const move = sourceSquare + targetSquare;
      const promotion = piece[1]?.toLowerCase() === "p" &&
        (targetSquare[1] === "8" || targetSquare[1] === "1")
        ? "q"
        : undefined;

      try {
        const result = gameInstance.move({
          from: sourceSquare,
          to: targetSquare,
          promotion,
        });

        if (!result) return false;

        const fullMove = promotion ? move + promotion : move;
        const timeSpent = Date.now() - lastMoveTime;

        setPosition(gameInstance.fen());
        setIsWhiteTurn(!isWhiteTurn);
        setLastMoveTime(Date.now());

        sendMove(fullMove, timeSpent);
        return true;
      } catch {
        return false;
      }
    },
    [gameInstance, gameOver, isMyTurn, isWhiteTurn, lastMoveTime, sendMove]
  );

  const getResultText = () => {
    if (!result) return "";
    switch (result) {
      case "white_win":
        return "White wins!";
      case "black_win":
        return "Black wins!";
      case "draw":
        return "Draw";
      case "abandoned":
        return "Game abandoned";
    }
  };

  const opponent = playerColor === "white" ? game.black_player : game.white_player;
  const self = playerColor === "white" ? game.white_player : game.black_player;

  return (
    <div className="container mx-auto px-4 py-4">
      <div className="max-w-2xl mx-auto">
        {/* Opponent info */}
        <div className="flex items-center justify-between mb-2 px-2">
          <div className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src={opponent?.avatar_url || undefined} />
              <AvatarFallback>
                {opponent?.username?.[0]?.toUpperCase() || "?"}
              </AvatarFallback>
            </Avatar>
            <span className="font-medium">
              {opponent?.username || "Waiting..."}
            </span>
          </div>
          <ChessClock
            time={playerColor === "white" ? blackTime : whiteTime}
            isRunning={!gameOver && !isMyTurn && game.status === "active"}
            onTimeout={() => handleTimeout(playerColor === "white" ? "black" : "white")}
          />
        </div>

        {/* Board */}
        <Card className="p-2">
          <CardContent className="p-0">
            <Chessboard
              position={position}
              onPieceDrop={onDrop}
              boardOrientation={playerColor || "white"}
              arePiecesDraggable={!gameOver && isMyTurn}
              customBoardStyle={{
                borderRadius: "4px",
              }}
              customDarkSquareStyle={{
                backgroundColor: "#779556",
              }}
              customLightSquareStyle={{
                backgroundColor: "#ebecd0",
              }}
            />
          </CardContent>
        </Card>

        {/* Self info */}
        <div className="flex items-center justify-between mt-2 px-2">
          <div className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src={self?.avatar_url || undefined} />
              <AvatarFallback>
                {self?.username?.[0]?.toUpperCase() || "?"}
              </AvatarFallback>
            </Avatar>
            <span className="font-medium">{self?.username || "You"}</span>
          </div>
          <ChessClock
            time={playerColor === "white" ? whiteTime : blackTime}
            isRunning={!gameOver && isMyTurn && game.status === "active"}
            onTimeout={() => handleTimeout(playerColor || "white")}
          />
        </div>

        {/* Game status */}
        <div className="mt-4 text-center">
          {gameOver ? (
            <div className="text-lg font-semibold">{getResultText()}</div>
          ) : (
            <div className="text-muted-foreground">
              {isMyTurn ? "Your turn" : "Opponent's turn"}
            </div>
          )}
        </div>

        {/* Actions */}
        {!gameOver && !isSpectator && (
          <div className="flex justify-center gap-2 mt-4">
            <Button variant="destructive" size="sm" onClick={handleResign}>
              <Flag className="h-4 w-4 mr-2" />
              Resign
            </Button>
          </div>
        )}

        {/* Game info */}
        <div className="text-center text-sm text-muted-foreground mt-4">
          {TIME_CONTROL_LABELS[game.time_control]} • Move {game.move_count}
        </div>
      </div>
    </div>
  );
}
