"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/hooks/use-user";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  getLessonsWithProgress,
  getCategoryProgress,
  LessonWithProgressResponse,
  CategoryProgressResponse,
  LessonCategory,
  LESSON_CATEGORY_LABELS,
} from "@/lib/api";
import { Loader2, BookOpen, CheckCircle, PlayCircle } from "lucide-react";

export default function LearnPage() {
  const router = useRouter();
  const { discordId, isAuthenticated, status } = useUser();

  const [lessons, setLessons] = useState<LessonWithProgressResponse[]>([]);
  const [categoryProgress, setCategoryProgress] = useState<CategoryProgressResponse[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<LessonCategory | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (!discordId) return;

    async function fetchData() {
      setIsLoading(true);
      try {
        const [lessonsData, progressData] = await Promise.all([
          getLessonsWithProgress(discordId, selectedCategory || undefined),
          getCategoryProgress(discordId),
        ]);
        setLessons(lessonsData);
        setCategoryProgress(progressData);
      } catch (error) {
        console.error("Failed to fetch lessons:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, [discordId, selectedCategory]);

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

  const getStatusIcon = (status: string | undefined) => {
    if (status === "completed") {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    if (status === "in_progress") {
      return <PlayCircle className="h-5 w-5 text-blue-500" />;
    }
    return <BookOpen className="h-5 w-5 text-gray-400" />;
  };

  const getProgressPercent = (current: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((current / total) * 100);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Nauka szachów</h1>
        <p className="text-gray-600">
          Ucz się krok po kroku, wykonując ruchy na interaktywnej szachownicy
        </p>
      </div>

      {/* Category Progress */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {categoryProgress.map((cat) => {
          const label = LESSON_CATEGORY_LABELS[cat.category];
          const percent = getProgressPercent(cat.completed_lessons, cat.total_lessons);
          const isSelected = selectedCategory === cat.category;

          return (
            <Card
              key={cat.category}
              className={`cursor-pointer transition-all ${
                isSelected ? "ring-2 ring-blue-500" : "hover:shadow-md"
              }`}
              onClick={() =>
                setSelectedCategory(isSelected ? null : cat.category)
              }
            >
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-1">{label.icon}</div>
                <div className="font-medium">{label.name}</div>
                <div className="text-sm text-gray-500">
                  {cat.completed_lessons}/{cat.total_lessons}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Lessons List */}
      <div className="space-y-4">
        {lessons.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-gray-500">
              Brak lekcji w tej kategorii
            </CardContent>
          </Card>
        ) : (
          lessons.map(({ lesson, progress }) => (
            <Card
              key={lesson.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => router.push(`/learn/${lesson.id}`)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(progress?.status)}
                    <div>
                      <CardTitle className="text-lg">{lesson.title}</CardTitle>
                      <CardDescription>
                        {LESSON_CATEGORY_LABELS[lesson.category].icon}{" "}
                        {LESSON_CATEGORY_LABELS[lesson.category].name} •{" "}
                        {lesson.steps_count} kroków
                      </CardDescription>
                    </div>
                  </div>
                  <Button
                    variant={progress?.status === "completed" ? "outline" : "default"}
                    size="sm"
                  >
                    {progress?.status === "completed"
                      ? "Powtórz"
                      : progress?.status === "in_progress"
                      ? "Kontynuuj"
                      : "Rozpocznij"}
                  </Button>
                </div>
              </CardHeader>
              {progress && progress.status === "in_progress" && (
                <CardContent className="pt-0">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>
                      Krok {progress.current_step_index + 1} z {progress.total_steps}
                    </span>
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full"
                        style={{
                          width: `${getProgressPercent(
                            progress.current_step_index,
                            progress.total_steps
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
