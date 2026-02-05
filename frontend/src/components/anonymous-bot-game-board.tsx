"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Chessboard } from "react-chessboard";
import { Chess, Square } from "chess.js";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BOT_DIFFICULTY_LABELS, BotDifficulty } from "@/lib/api";
import { getStockfish, StockfishBrowser } from "@/lib/stockfish-browser";
import { Flag, RotateCcw, Bot, Loader2 } from "lucide-react";

interface AnonymousBotGameBoardProps {
  difficulty: BotDifficulty;
  playerColor: "white" | "black";
  onNewGame: () => void;
}

type GameResult = "white_win" | "black_win" | "draw" | null;

export function AnonymousBotGameBoard({
  difficulty,
  playerColor,
  onNewGame,
}: AnonymousBotGameBoardProps) {
  const [gameInstance] = useState(() => new Chess());
  const [position, setPosition] = useState(gameInstance.fen());
  const [isThinking, setIsThinking] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [result, setResult] = useState<GameResult>(null);
  const [moveCount, setMoveCount] = useState(0);
  const [stockfishReady, setStockfishReady] = useState(false);
  const stockfishRef = useRef<StockfishBrowser | null>(null);

  // Initialize Stockfish
  useEffect(() => {
    const initStockfish = async () => {
      try {
        const sf = getStockfish();
        stockfishRef.current = sf;
        await sf.init();
        sf.setDifficulty(difficulty);
        setStockfishReady(true);

        // If bot plays first (player is black), make bot move
        if (playerColor === "black") {
          makeBotMove(sf, gameInstance.fen());
        }
      } catch (error) {
        console.error("Failed to initialize Stockfish:", error);
      }
    };

    initStockfish();

    return () => {
      if (stockfishRef.current) {
        stockfishRef.current.stop();
      }
    };
  }, [difficulty, playerColor]);

  const makeBotMove = useCallback((sf: StockfishBrowser, fen: string) => {
    setIsThinking(true);
    sf.getBestMove(fen, (bestMove) => {
      const from = bestMove.slice(0, 2) as Square;
      const to = bestMove.slice(2, 4) as Square;
      const promotion = bestMove.length > 4 ? bestMove[4] : undefined;

      try {
        gameInstance.move({ from, to, promotion });
        setPosition(gameInstance.fen());
        setMoveCount((prev) => prev + 1);

        // Check for game end
        if (gameInstance.isGameOver()) {
          setGameOver(true);
          if (gameInstance.isCheckmate()) {
            // Bot just moved and checkmated, so bot wins
            setResult(playerColor === "white" ? "black_win" : "white_win");
          } else {
            setResult("draw");
          }
        }
      } catch (error) {
        console.error("Invalid bot move:", bestMove, error);
      }

      setIsThinking(false);
    });
  }, [gameInstance, playerColor]);

  const isMyTurn = useCallback(() => {
    const currentTurn = gameInstance.turn();
    return (
      (currentTurn === "w" && playerColor === "white") ||
      (currentTurn === "b" && playerColor === "black")
    );
  }, [gameInstance, playerColor]);

  const onDrop = useCallback(
    (sourceSquare: Square, targetSquare: Square, piece: string): boolean => {
      if (!stockfishReady || isThinking || gameOver || !isMyTurn()) {
        return false;
      }

      const promotion =
        piece[1]?.toLowerCase() === "p" &&
        (targetSquare[1] === "8" || targetSquare[1] === "1")
          ? "q"
          : undefined;

      try {
        gameInstance.move({
          from: sourceSquare,
          to: targetSquare,
          promotion,
        });
      } catch {
        return false;
      }

      setPosition(gameInstance.fen());
      setMoveCount((prev) => prev + 1);

      // Check for game end after player move
      if (gameInstance.isGameOver()) {
        setGameOver(true);
        if (gameInstance.isCheckmate()) {
          // Player just moved and checkmated, so player wins
          setResult(playerColor === "white" ? "white_win" : "black_win");
        } else {
          setResult("draw");
        }
        return true;
      }

      // Make bot move
      if (stockfishRef.current) {
        makeBotMove(stockfishRef.current, gameInstance.fen());
      }

      return true;
    },
    [gameInstance, stockfishReady, isThinking, gameOver, isMyTurn, playerColor, makeBotMove]
  );

  const handleResign = () => {
    setGameOver(true);
    setResult(playerColor === "white" ? "black_win" : "white_win");
  };

  const getResultText = () => {
    if (!result) return "";
    const playerWon =
      (playerColor === "white" && result === "white_win") ||
      (playerColor === "black" && result === "black_win");
    if (playerWon) return "You win!";
    if (result === "draw") return "Draw";
    return "Bot wins!";
  };

  const difficultyInfo = BOT_DIFFICULTY_LABELS[difficulty];
  const canMove = stockfishReady && !isThinking && !gameOver && isMyTurn();

  if (!stockfishReady) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="text-muted-foreground">Loading Stockfish...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Bot info */}
      <div className="flex items-center gap-2 text-muted-foreground">
        <Bot className="h-5 w-5" />
        <span>
          Stockfish ({difficultyInfo.name}) ~{difficultyInfo.elo}
        </span>
      </div>

      {/* Board */}
      <Card className="p-2">
        <CardContent className="p-0 relative">
          <Chessboard
            position={position}
            onPieceDrop={onDrop}
            boardOrientation={playerColor}
            boardWidth={400}
            arePiecesDraggable={canMove}
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
        You ({playerColor === "white" ? "White" : "Black"}) - Guest
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
        ) : canMove ? (
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

        <Button variant="outline" size="sm" onClick={onNewGame}>
          <RotateCcw className="h-4 w-4 mr-2" />
          New Game
        </Button>
      </div>

      {/* Move count */}
      <div className="text-sm text-muted-foreground">
        Move {Math.ceil(moveCount / 2)}
      </div>

      {/* Anonymous note */}
      <p className="text-xs text-muted-foreground text-center max-w-xs">
        Playing as guest. Log in to save your games and track statistics.
      </p>
    </div>
  );
}
