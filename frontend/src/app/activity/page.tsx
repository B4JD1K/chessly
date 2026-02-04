"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useDiscord } from "@/contexts/discord-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Puzzle, Bot, Users, Trophy, BookOpen } from "lucide-react";

export default function ActivityPage() {
  const router = useRouter();
  const { isInDiscord, isAuthenticated, user, setActivity } = useDiscord();

  useEffect(() => {
    // Redirect if not in Discord
    if (!isInDiscord) {
      router.push("/");
      return;
    }

    // Set Discord activity status
    if (isAuthenticated) {
      setActivity("Browsing Chessly", "Choosing game mode");
    }
  }, [isInDiscord, isAuthenticated, router, setActivity]);

  const handleNavigate = (path: string, activityText: string) => {
    setActivity("Playing Chessly", activityText);
    router.push(path);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">♟️ Chessly</h1>
        {user && (
          <p className="text-gray-400">
            Witaj, <span className="text-blue-400">{user.global_name || user.username}</span>!
          </p>
        )}
      </div>

      <div className="grid gap-4">
        <Card
          className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
          onClick={() => handleNavigate("/puzzle/daily", "Solving daily puzzle")}
        >
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-white">
              <Puzzle className="h-5 w-5 text-yellow-500" />
              Puzzle dnia
            </CardTitle>
            <CardDescription className="text-gray-400">
              Rozwiąż dzisiejszy puzzle i buduj streak
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full">
              Rozwiąż puzzle
            </Button>
          </CardContent>
        </Card>

        <Card
          className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
          onClick={() => handleNavigate("/learn", "Learning chess")}
        >
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-white">
              <BookOpen className="h-5 w-5 text-emerald-500" />
              Nauka szachów
            </CardTitle>
            <CardDescription className="text-gray-400">
              Interaktywne lekcje krok po kroku
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full">
              Rozpocznij naukę
            </Button>
          </CardContent>
        </Card>

        <Card
          className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
          onClick={() => handleNavigate("/play/bot", "Playing vs bot")}
        >
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-white">
              <Bot className="h-5 w-5 text-green-500" />
              Graj z botem
            </CardTitle>
            <CardDescription className="text-gray-400">
              Trenuj z Stockfishem na różnych poziomach trudności
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full">
              Wybierz poziom
            </Button>
          </CardContent>
        </Card>

        <Card
          className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
          onClick={() => handleNavigate("/play", "Looking for opponent")}
        >
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-white">
              <Users className="h-5 w-5 text-blue-500" />
              Graj z innym graczem
            </CardTitle>
            <CardDescription className="text-gray-400">
              Stwórz pokój lub dołącz do gry znajomego
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full">
              Rozpocznij grę
            </Button>
          </CardContent>
        </Card>

        <Card
          className="bg-gray-800 border-gray-700 cursor-pointer hover:bg-gray-750 transition-colors"
          onClick={() => handleNavigate("/profile", "Viewing achievements")}
        >
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-white">
              <Trophy className="h-5 w-5 text-amber-500" />
              Profil i osiągnięcia
            </CardTitle>
            <CardDescription className="text-gray-400">
              Sprawdź swoje statystyki i odblokowane osiągnięcia
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full">
              Zobacz profil
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
