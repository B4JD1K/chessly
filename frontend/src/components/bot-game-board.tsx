"use client";

import { useState, useCallback } from "react";
import { Chessboard } from "react-chessboard";
import { Chess, Square } from "chess.js";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BotGameResponse,
  BotMoveResponse,
  GameResult,
  makeBotMove,
  resignBotGame,
  getBotGamePGN,
  BOT_DIFFICULTY_LABELS,
} from "@/lib/api";
import { Flag, Download, RotateCcw, Bot, Loader2 } from "lucide-react";

interface BotGameBoardProps {
  game: BotGameResponse;
  discordId: string;
  onGameUpdate: (game: Partial<BotGameResponse>) => void;
}

export function BotGameBoard({ game, discordId, onGameUpdate }: BotGameBoardProps) {
  const [position, setPosition] = useState(game.current_fen);
  const [gameInstance] = useState(() => new Chess(game.current_fen));
  const [isThinking, setIsThinking] = useState(false);
  const [gameOver, setGameOver] = useState(game.status === "completed");
  const [result, setResult] = useState<GameResult | null>(game.result);
  const [lastBotMove, setLastBotMove] = useState<string | null>(null);

  const isMyTurn = game.is_player_turn && !gameOver && !isThinking;

  const onDrop = useCallback(
    (sourceSquare: Square, targetSquare: Square, piece: string): boolean => {
      if (!isMyTurn) return false;

      const move = sourceSquare + targetSquare;
      const promotion = piece[1]?.toLowerCase() === "p" &&
        (targetSquare[1] === "8" || targetSquare[1] === "1")
        ? "q"
        : undefined;

      // Try move locally first
      try {
        gameInstance.move({
          from: sourceSquare,
          to: targetSquare,
          promotion,
        });
      } catch {
        return false;
      }

      const fullMove = promotion ? move + promotion : move;
      const currentPosition = position;
      setPosition(gameInstance.fen());
      setIsThinking(true);

      // Handle API call asynchronously
      makeBotMove(game.id, fullMove, discordId)
        .then((response) => {
          if (response.valid) {
            // Apply bot's response move if any
            if (response.bot_move_uci && response.fen_after) {
              gameInstance.load(response.fen_after);
              setPosition(response.fen_after);
              setLastBotMove(response.bot_move_uci);
            }

            if (response.game_over) {
              setGameOver(true);
              setResult(response.result);
              onGameUpdate({
                status: "completed",
                result: response.result,
                current_fen: response.fen_after || currentPosition,
              });
            } else {
              onGameUpdate({
                current_fen: response.fen_after || currentPosition,
                is_player_turn: true,
              });
            }
          } else {
            // Revert move
            gameInstance.load(currentPosition);
            setPosition(currentPosition);
          }
        })
        .catch((error) => {
          console.error("Move error:", error);
          gameInstance.load(currentPosition);
          setPosition(currentPosition);
        })
        .finally(() => {
          setIsThinking(false);
        });

      return true;
    },
    [game.id, discordId, gameInstance, isMyTurn, position, onGameUpdate]
  );

  const handleResign = async () => {
    try {
      await resignBotGame(game.id, discordId);
      const newResult = game.player_color === "white" ? "black_win" : "white_win";
      setGameOver(true);
      setResult(newResult as GameResult);
      onGameUpdate({ status: "completed", result: newResult as GameResult });
    } catch (error) {
      console.error("Resign error:", error);
    }
  };

  const handleDownloadPGN = async () => {
    try {
      const pgn = await getBotGamePGN(game.id);
      const blob = new Blob([pgn], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chessly-bot-game-${game.id}.pgn`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("PGN download error:", error);
    }
  };

  const getResultText = () => {
    if (!result) return "";
    const playerWon = (game.player_color === "white" && result === "white_win") ||
                      (game.player_color === "black" && result === "black_win");
    if (playerWon) return "You win!";
    if (result === "draw") return "Draw";
    return "Bot wins!";
  };

  const difficultyInfo = BOT_DIFFICULTY_LABELS[game.difficulty];

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Bot info */}
      <div className="flex items-center gap-2 text-muted-foreground">
        <Bot className="h-5 w-5" />
        <span>Stockfish ({difficultyInfo.name}) ~{difficultyInfo.elo}</span>
      </div>

      {/* Board */}
      <Card className="p-2">
        <CardContent className="p-0 relative">
          <Chessboard
            position={position}
            onPieceDrop={onDrop}
            boardOrientation={game.player_color}
            boardWidth={400}
            arePiecesDraggable={isMyTurn}
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

      {/* Player info */}
      <div className="text-muted-foreground">
        You ({game.player_color === "white" ? "White" : "Black"})
      </div>

      {/* Status */}
      <div className="text-center h-8">
        {gameOver ? (
          <div className="text-lg font-semibold">{getResultText()}</div>
        ) : isThinking ? (
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Bot is thinking...</span>
          </div>
        ) : isMyTurn ? (
          <div className="text-muted-foreground">Your turn</div>
        ) : (
          <div className="text-muted-foreground">Waiting...</div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {!gameOver && (
          <Button variant="destructive" size="sm" onClick={handleResign}>
            <Flag className="h-4 w-4 mr-2" />
            Resign
          </Button>
        )}

        {gameOver && (
          <Button variant="outline" size="sm" onClick={handleDownloadPGN}>
            <Download className="h-4 w-4 mr-2" />
            Download PGN
          </Button>
        )}
      </div>

      {/* Move count */}
      <div className="text-sm text-muted-foreground">
        Move {Math.ceil(game.move_count / 2)}
      </div>
    </div>
  );
}
