"use client";

import { useState, useCallback, useEffect } from "react";
import { Chessboard } from "react-chessboard";
import { Chess, Square } from "chess.js";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  validateLessonMove,
  LessonDetailResponse,
  LessonProgressResponse,
} from "@/lib/api";
import { CheckCircle, XCircle, Lightbulb, ArrowRight } from "lucide-react";

interface LessonBoardProps {
  lesson: LessonDetailResponse;
  progress: LessonProgressResponse;
  discordId: string;
  onProgressUpdate: (progress: LessonProgressResponse) => void;
  onLessonComplete: () => void;
}

export function LessonBoard({
  lesson,
  progress,
  discordId,
  onProgressUpdate,
  onLessonComplete,
}: LessonBoardProps) {
  const currentStep = lesson.steps[progress.current_step_index];
  const [game, setGame] = useState(new Chess(currentStep?.fen || ""));
  const [feedback, setFeedback] = useState<{
    type: "success" | "error" | "info";
    message: string;
  } | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [isComplete, setIsComplete] = useState(progress.status === "completed");

  // Determine board orientation based on whose turn it is
  const boardOrientation = game.turn() === "w" ? "white" : "black";

  useEffect(() => {
    if (currentStep) {
      setGame(new Chess(currentStep.fen));
      setFeedback(null);
      setShowHint(false);
    }
  }, [currentStep]);

  const onDrop = useCallback(
    async (sourceSquare: Square, targetSquare: Square) => {
      if (isValidating || isComplete) return false;

      // Check if move is legal locally first
      const gameCopy = new Chess(game.fen());
      try {
        const move = gameCopy.move({
          from: sourceSquare,
          to: targetSquare,
          promotion: "q", // Always promote to queen for simplicity
        });

        if (!move) return false;
      } catch {
        return false;
      }

      // Build UCI move string
      let moveUci = `${sourceSquare}${targetSquare}`;

      // Add promotion if applicable
      const piece = game.get(sourceSquare);
      if (piece?.type === "p") {
        const targetRank = targetSquare[1];
        if (
          (piece.color === "w" && targetRank === "8") ||
          (piece.color === "b" && targetRank === "1")
        ) {
          moveUci += "q"; // Promote to queen
        }
      }

      setIsValidating(true);

      try {
        const result = await validateLessonMove(lesson.id, moveUci, discordId);

        if (result.correct) {
          // Update the board with the new position
          if (result.fen_after) {
            setGame(new Chess(result.fen_after));
          } else {
            // Apply the move locally
            const newGame = new Chess(game.fen());
            newGame.move({
              from: sourceSquare,
              to: targetSquare,
              promotion: "q",
            });
            setGame(newGame);
          }

          if (result.is_lesson_complete) {
            setIsComplete(true);
            setFeedback({
              type: "success",
              message: "🎉 Gratulacje! Lekcja ukończona!",
            });
            onLessonComplete();
          } else {
            setFeedback({
              type: "success",
              message: result.opponent_move
                ? `Poprawnie! ${result.message || ""}`
                : result.message || "Poprawnie!",
            });

            // Update progress
            if (result.next_step_index !== null) {
              onProgressUpdate({
                ...progress,
                current_step_index: result.next_step_index,
              });
            }
          }
        } else {
          setFeedback({
            type: "error",
            message: result.message || "Spróbuj ponownie",
          });
        }
      } catch (error) {
        setFeedback({
          type: "error",
          message: "Wystąpił błąd. Spróbuj ponownie.",
        });
      } finally {
        setIsValidating(false);
      }

      return true;
    },
    [game, lesson.id, discordId, isValidating, isComplete, onProgressUpdate, onLessonComplete, progress]
  );

  if (!currentStep && !isComplete) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">Brak kroków w tej lekcji</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Chessboard */}
      <div className="aspect-square">
        <Chessboard
          position={game.fen()}
          onPieceDrop={onDrop}
          boardOrientation={boardOrientation}
          arePiecesDraggable={!isComplete && !isValidating}
          customBoardStyle={{
            borderRadius: "8px",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          }}
        />
      </div>

      {/* Instructions and Feedback */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>
                Krok {progress.current_step_index + 1} z {lesson.steps.length}
              </span>
              <span className="text-sm font-normal text-gray-500">
                {lesson.title}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all"
                style={{
                  width: `${
                    ((progress.current_step_index + (isComplete ? 1 : 0)) /
                      lesson.steps.length) *
                    100
                  }%`,
                }}
              />
            </div>

            {/* Instruction */}
            {!isComplete && currentStep && (
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-blue-900">{currentStep.instruction}</p>
              </div>
            )}

            {/* Feedback */}
            {feedback && (
              <div
                className={`p-4 rounded-lg flex items-start gap-3 ${
                  feedback.type === "success"
                    ? "bg-green-50 text-green-900"
                    : feedback.type === "error"
                    ? "bg-red-50 text-red-900"
                    : "bg-gray-50 text-gray-900"
                }`}
              >
                {feedback.type === "success" ? (
                  <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                ) : feedback.type === "error" ? (
                  <XCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                ) : null}
                <p>{feedback.message}</p>
              </div>
            )}

            {/* Hint */}
            {!isComplete && currentStep?.hint && (
              <div>
                {showHint ? (
                  <div className="p-4 bg-yellow-50 rounded-lg flex items-start gap-3">
                    <Lightbulb className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <p className="text-yellow-900">{currentStep.hint}</p>
                  </div>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowHint(true)}
                  >
                    <Lightbulb className="h-4 w-4 mr-2" />
                    Pokaż podpowiedź
                  </Button>
                )}
              </div>
            )}

            {/* Complete button */}
            {isComplete && (
              <Button className="w-full" onClick={onLessonComplete}>
                <ArrowRight className="h-4 w-4 mr-2" />
                Wróć do listy lekcji
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
