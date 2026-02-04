"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/hooks/use-user";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getUserAchievements,
  getUserStats,
  UserAchievementsListResponse,
  UserStatsResponse,
} from "@/lib/api";
import { Loader2, Trophy, Target, BookOpen, Swords, Flame } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function ProfilePage() {
  const router = useRouter();
  const { discordId, username, avatarUrl, isAuthenticated, status, streak } = useUser();

  const [achievements, setAchievements] = useState<UserAchievementsListResponse | null>(null);
  const [stats, setStats] = useState<UserStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (!discordId) return;

    const userId = discordId; // Capture for closure

    async function fetchData() {
      setIsLoading(true);
      try {
        const [achievementsData, statsData] = await Promise.all([
          getUserAchievements(userId),
          getUserStats(userId),
        ]);
        setAchievements(achievementsData);
        setStats(statsData);
      } catch (error) {
        console.error("Failed to fetch profile data:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, [discordId]);

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

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* User Info */}
      <Card className="mb-8">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={avatarUrl || undefined} alt={username || "User"} />
              <AvatarFallback>{username?.charAt(0).toUpperCase() || "U"}</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-2xl font-bold">{username}</h1>
              <p className="text-gray-600">
                {achievements?.total_unlocked || 0} / {achievements?.total_available || 0} osiągnięć
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <Target className="h-8 w-8 mx-auto mb-2 text-blue-500" />
            <div className="text-2xl font-bold">{stats?.puzzles_solved || 0}</div>
            <div className="text-sm text-gray-500">Puzzli rozwiązanych</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <BookOpen className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <div className="text-2xl font-bold">{stats?.lessons_completed || 0}</div>
            <div className="text-sm text-gray-500">Lekcji ukończonych</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <Swords className="h-8 w-8 mx-auto mb-2 text-purple-500" />
            <div className="text-2xl font-bold">{stats?.games_won || 0}</div>
            <div className="text-sm text-gray-500">Gier wygranych</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 text-center">
            <Flame className="h-8 w-8 mx-auto mb-2 text-orange-500" />
            <div className="text-2xl font-bold">{stats?.best_streak || 0}</div>
            <div className="text-sm text-gray-500">Najlepszy streak</div>
          </CardContent>
        </Card>
      </div>

      {/* Achievements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            Osiągnięcia
          </CardTitle>
          <CardDescription>
            Odblokowane: {achievements?.total_unlocked || 0} / {achievements?.total_available || 0}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Unlocked Achievements */}
          {achievements && achievements.unlocked.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-3">Odblokowane</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {achievements.unlocked.map(({ achievement, unlocked_at }) => (
                  <div
                    key={achievement.id}
                    className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg"
                  >
                    <div className="text-2xl">{achievement.icon || "🏆"}</div>
                    <div className="flex-1">
                      <div className="font-medium">{achievement.name}</div>
                      <div className="text-sm text-gray-600">{achievement.description}</div>
                      <div className="text-xs text-gray-400">
                        {new Date(unlocked_at).toLocaleDateString("pl-PL")}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Locked Achievements */}
          {achievements && achievements.locked.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-3">Do odblokowania</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {achievements.locked.map((achievement) => (
                  <div
                    key={achievement.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg opacity-60"
                  >
                    <div className="text-2xl grayscale">{achievement.icon || "🔒"}</div>
                    <div className="flex-1">
                      <div className="font-medium">{achievement.name}</div>
                      <div className="text-sm text-gray-600">{achievement.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {achievements && achievements.unlocked.length === 0 && achievements.locked.length === 0 && (
            <p className="text-center text-gray-500 py-8">
              Brak dostępnych osiągnięć
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
