"use client";

import Link from "next/link";
import { signIn, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Flame, User, LogOut } from "lucide-react";
import { useUser } from "@/hooks/use-user";

export function Header() {
  const { session, status, streak, username, avatarUrl } = useUser();

  return (
    <header className="border-b">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">♞</span>
          <span className="text-xl font-bold">Chessly</span>
        </Link>

        <nav className="flex items-center gap-4">
          <Link
            href="/puzzle/daily"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            Puzzle
          </Link>
          <Link
            href="/learn"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            Nauka
          </Link>
          <Link
            href="/play"
            className="text-sm font-medium hover:text-primary transition-colors"
          >
            Graj
          </Link>

          {status === "loading" ? (
            <div className="h-10 w-10 rounded-full bg-muted animate-pulse" />
          ) : session ? (
            <div className="flex items-center gap-3">
              <div
                className="flex items-center gap-1 text-orange-500"
                title={`Best streak: ${streak?.best_streak || 0}`}
              >
                <Flame className="h-4 w-4" />
                <span className="text-sm font-medium">
                  {streak?.current_streak || 0}
                </span>
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                    <Avatar className="h-9 w-9">
                      <AvatarImage src={avatarUrl || session.user?.image || undefined} />
                      <AvatarFallback>
                        {(username || session.user?.name)?.[0]?.toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem asChild>
                    <Link href="/profile" className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Profil i Osiągnięcia
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => signOut()} className="flex items-center gap-2">
                    <LogOut className="h-4 w-4" />
                    Wyloguj
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <Button onClick={() => signIn("discord")}>
              Zaloguj przez Discord
            </Button>
          )}
        </nav>
      </div>
    </header>
  );
}
