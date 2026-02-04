"use client";

import { useEffect, useState, useRef } from "react";
import { cn } from "@/lib/utils";

interface ChessClockProps {
  time: number; // Time in seconds
  isRunning: boolean;
  onTimeout?: () => void;
}

function formatTime(seconds: number): string {
  if (seconds < 0) seconds = 0;

  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;

  if (mins >= 60) {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return `${hours}:${remainingMins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }

  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function ChessClock({ time, isRunning, onTimeout }: ChessClockProps) {
  const [displayTime, setDisplayTime] = useState(time);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const hasTimedOut = useRef(false);

  // Sync with prop changes
  useEffect(() => {
    setDisplayTime(time);
    hasTimedOut.current = false;
  }, [time]);

  // Handle countdown
  useEffect(() => {
    if (isRunning && displayTime > 0) {
      intervalRef.current = setInterval(() => {
        setDisplayTime((prev) => {
          const newTime = prev - 1;
          if (newTime <= 0 && !hasTimedOut.current) {
            hasTimedOut.current = true;
            onTimeout?.();
            return 0;
          }
          return newTime;
        });
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, displayTime, onTimeout]);

  const isLowTime = displayTime <= 30;
  const isCriticalTime = displayTime <= 10;

  return (
    <div
      className={cn(
        "px-3 py-1.5 rounded-md font-mono text-lg font-semibold min-w-[80px] text-center",
        isRunning
          ? isCriticalTime
            ? "bg-red-500 text-white animate-pulse"
            : isLowTime
            ? "bg-orange-500 text-white"
            : "bg-primary text-primary-foreground"
          : "bg-muted text-muted-foreground"
      )}
    >
      {formatTime(displayTime)}
    </div>
  );
}
