"use client";

import { useSession } from "next-auth/react";
import { useEffect, useState, useCallback } from "react";
import { syncUser, getStreak, StreakResponse } from "@/lib/api";
import { useDiscord } from "@/contexts/discord-context";

export function useUser() {
  const { data: session, status } = useSession();
  const { isInDiscord, isAuthenticated: isDiscordAuth, user: discordUser } = useDiscord();

  const [streak, setStreak] = useState<StreakResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSynced, setIsSynced] = useState(false);

  // Get discord ID from either source
  const discordId = isInDiscord && discordUser
    ? discordUser.id
    : (session?.user as any)?.discordId as string | undefined;

  // Get user name from either source
  const username = isInDiscord && discordUser
    ? discordUser.global_name || discordUser.username
    : session?.user?.name;

  // Get avatar from either source
  const avatarUrl = isInDiscord && discordUser
    ? discordUser.avatar
      ? `https://cdn.discordapp.com/avatars/${discordUser.id}/${discordUser.avatar}.png`
      : null
    : session?.user?.image;

  // Check if authenticated in any way
  const isAuthenticated = isInDiscord ? isDiscordAuth : status === "authenticated";

  // Sync user with backend after login
  useEffect(() => {
    if (!isAuthenticated || !discordId || isSynced) return;

    const sync = async () => {
      try {
        await syncUser({
          discord_id: discordId,
          username: username || "Unknown",
          avatar_url: avatarUrl,
        });
        setIsSynced(true);
      } catch (error) {
        console.error("Failed to sync user:", error);
      }
    };

    sync();
  }, [isAuthenticated, discordId, username, avatarUrl, isSynced]);

  // Fetch streak
  const refreshStreak = useCallback(async () => {
    if (!discordId) return;

    setIsLoading(true);
    try {
      const data = await getStreak(discordId);
      setStreak(data);
    } catch (error) {
      console.error("Failed to fetch streak:", error);
    } finally {
      setIsLoading(false);
    }
  }, [discordId]);

  // Fetch streak when synced
  useEffect(() => {
    if (isSynced && discordId) {
      refreshStreak();
    }
  }, [isSynced, discordId, refreshStreak]);

  return {
    session,
    status: isInDiscord ? (isDiscordAuth ? "authenticated" : "unauthenticated") : status,
    isAuthenticated,
    discordId,
    username,
    avatarUrl,
    streak,
    isLoading,
    refreshStreak,
  };
}
