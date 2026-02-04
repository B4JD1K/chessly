"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { useUser } from "@/hooks/use-user";
import { LessonBoard } from "@/components/lesson-board";
import { Button } from "@/components/ui/button";
import {
  getLesson,
  getLessonProgress,
  startLesson,
  LessonDetailResponse,
  LessonProgressResponse,
  LESSON_CATEGORY_LABELS,
} from "@/lib/api";
import { Loader2, ArrowLeft } from "lucide-react";

export default function LessonPage() {
  const router = useRouter();
  const params = useParams();
  const lessonId = parseInt(params.id as string);
  const { discordId, isAuthenticated, status } = useUser();

  const [lesson, setLesson] = useState<LessonDetailResponse | null>(null);
  const [progress, setProgress] = useState<LessonProgressResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (!discordId || !lessonId) return;

    const userId = discordId; // Capture for closure

    async function fetchData() {
      setIsLoading(true);
      setError(null);

      try {
        const [lessonData, progressData] = await Promise.all([
          getLesson(lessonId),
          getLessonProgress(lessonId, userId),
        ]);

        setLesson(lessonData);

        // If not started, start the lesson
        if (progressData.status === "not_started") {
          const newProgress = await startLesson(lessonId, userId);
          setProgress(newProgress);
        } else {
          setProgress(progressData);
        }
      } catch (err) {
        console.error("Failed to fetch lesson:", err);
        setError("Nie udało się załadować lekcji");
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, [discordId, lessonId]);

  const handleProgressUpdate = useCallback((newProgress: LessonProgressResponse) => {
    setProgress(newProgress);
  }, []);

  const handleLessonComplete = useCallback(() => {
    router.push("/learn");
  }, [router]);

  if (status === "loading" || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={() => router.push("/learn")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Wróć do listy lekcji
          </Button>
        </div>
      </div>
    );
  }

  if (!lesson || !progress) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/learn")}
          className="mb-2"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Wróć do listy lekcji
        </Button>
        <h1 className="text-2xl font-bold">{lesson.title}</h1>
        <p className="text-gray-600">
          {LESSON_CATEGORY_LABELS[lesson.category].icon}{" "}
          {LESSON_CATEGORY_LABELS[lesson.category].name}
          {lesson.description && ` • ${lesson.description}`}
        </p>
      </div>

      {/* Lesson Board */}
      <LessonBoard
        lesson={lesson}
        progress={progress}
        discordId={discordId!}
        onProgressUpdate={handleProgressUpdate}
        onLessonComplete={handleLessonComplete}
      />
    </div>
  );
}
