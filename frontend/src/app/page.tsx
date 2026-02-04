import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-2xl mx-auto text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Solve Daily Chess Puzzles
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Improve your tactical skills with a new puzzle every day.
          Track your streak and compete with friends.
        </p>
        <Button asChild size="lg">
          <Link href="/puzzle/daily">
            Start Today&apos;s Puzzle
          </Link>
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">♟</span>
              Daily Puzzles
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              A new puzzle every day at midnight. Solve it to keep your streak alive.
            </CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">🔥</span>
              Streaks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Build your streak by solving puzzles daily. Don&apos;t break the chain!
            </CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="text-2xl">🎮</span>
              Discord
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Login with Discord and get notified about daily puzzles.
            </CardDescription>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
