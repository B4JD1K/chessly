"use client";

import { useState, useCallback, useEffect } from "react";
import { Chessboard } from "react-chessboard";
import { Chess, Square } from "chess.js";
import { validateMove, PuzzleResponse } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, RotateCcw } from "lucide-react";

interface PuzzleBoardProps {
  puzzle: PuzzleResponse;
  onComplete?: (success: boolean) => void;
}

type PuzzleStatus = "playing" | "success" | "failed";

export function PuzzleBoard({ puzzle, onComplete }: PuzzleBoardProps) {
  const [game, setGame] = useState<Chess>(() => new Chess(puzzle.fen));
  const [moveIndex, setMoveIndex] = useState(0);
  const [status, setStatus] = useState<PuzzleStatus>("playing");
  const [message, setMessage] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const boardOrientation = puzzle.player_color === "white" ? "white" : "black";

  const resetPuzzle = useCallback(() => {
    setGame(new Chess(puzzle.fen));
    setMoveIndex(0);
    setStatus("playing");
    setMessage(null);
  }, [puzzle.fen]);

  const makeOpponentMove = useCallback((move: string) => {
    setTimeout(() => {
      setGame((g) => {
        const newGame = new Chess(g.fen());
        try {
          newGame.move({
            from: move.slice(0, 2) as Square,
            to: move.slice(2, 4) as Square,
            promotion: move.length > 4 ? move[4] : undefined,
          });
        } catch {
          console.error("Invalid opponent move:", move);
        }
        return newGame;
      });
      setMoveIndex((i) => i + 2);
    }, 300);
  }, []);

  const onDrop = useCallback(
    async (sourceSquare: Square, targetSquare: Square, piece: string) => {
      if (status !== "playing" || isValidating) return false;

      const move = sourceSquare + targetSquare;
      const promotion = piece[1]?.toLowerCase() === "p" &&
        (targetSquare[1] === "8" || targetSquare[1] === "1")
        ? "q"
        : undefined;
      const fullMove = promotion ? move + promotion : move;

      // Try move locally first
      const gameCopy = new Chess(game.fen());
      try {
        gameCopy.move({
          from: sourceSquare,
          to: targetSquare,
          promotion,
        });
      } catch {
        return false;
      }

      setIsValidating(true);
      setGame(gameCopy);

      try {
        const response = await validateMove(puzzle.id, fullMove, moveIndex);

        if (response.correct) {
          if (response.is_complete) {
            setStatus("success");
            setMessage("Puzzle solved!");
            onComplete?.(true);
          } else if (response.opponent_move) {
            makeOpponentMove(response.opponent_move);
          }
        } else {
          // Revert move
          setGame(new Chess(game.fen()));
          setMessage(response.message || "Incorrect move");

          // Clear message after 2 seconds
          setTimeout(() => setMessage(null), 2000);
        }
      } catch (error) {
        console.error("Validation error:", error);
        setGame(new Chess(game.fen()));
        setMessage("Error validating move");
        setTimeout(() => setMessage(null), 2000);
      } finally {
        setIsValidating(false);
      }

      return true;
    },
    [game, puzzle.id, moveIndex, status, isValidating, makeOpponentMove, onComplete]
  );

  // Check if it's player's turn
  const isPlayerTurn = useCallback(() => {
    const turn = game.turn();
    return (turn === "w" && puzzle.player_color === "white") ||
           (turn === "b" && puzzle.player_color === "black");
  }, [game, puzzle.player_color]);

  return (
    <div className="flex flex-col items-center gap-4">
      <Card className="p-2">
        <CardContent className="p-0">
          <Chessboard
            position={game.fen()}
            onPieceDrop={onDrop}
            boardOrientation={boardOrientation}
            boardWidth={400}
            arePiecesDraggable={status === "playing" && isPlayerTurn() && !isValidating}
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

      <div className="flex items-center gap-4 h-10">
        {status === "success" && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">Puzzle solved!</span>
          </div>
        )}

        {status === "failed" && (
          <div className="flex items-center gap-2 text-red-600">
            <XCircle className="h-5 w-5" />
            <span className="font-medium">Puzzle failed</span>
          </div>
        )}

        {status === "playing" && message && (
          <div className="text-muted-foreground">{message}</div>
        )}

        {status === "playing" && !message && (
          <div className="text-muted-foreground">
            {isPlayerTurn() ? "Your turn" : "Opponent's turn..."}
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <Button variant="outline" onClick={resetPuzzle}>
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset
        </Button>
      </div>

      <div className="text-sm text-muted-foreground">
        Rating: {puzzle.rating} • {puzzle.themes.join(", ") || "Tactics"}
      </div>
    </div>
  );
}
