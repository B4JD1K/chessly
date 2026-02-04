"use client";

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { DiscordSDK, DiscordSDKMock } from "@discord/embedded-app-sdk";
import {
  DiscordAuth,
  DiscordUser,
  isRunningInDiscord,
  initializeDiscordSdk,
  setDiscordActivity,
} from "@/lib/discord";

interface DiscordContextType {
  isInDiscord: boolean;
  isLoading: boolean;
  isAuthenticated: boolean;
  sdk: DiscordSDK | DiscordSDKMock | null;
  user: DiscordUser | null;
  accessToken: string | null;
  error: string | null;
  setActivity: (details: string, state?: string) => Promise<void>;
}

const DiscordContext = createContext<DiscordContextType>({
  isInDiscord: false,
  isLoading: true,
  isAuthenticated: false,
  sdk: null,
  user: null,
  accessToken: null,
  error: null,
  setActivity: async () => {},
});

export function useDiscord() {
  return useContext(DiscordContext);
}

interface DiscordProviderProps {
  children: ReactNode;
}

export function DiscordProvider({ children }: DiscordProviderProps) {
  const [isInDiscord, setIsInDiscord] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sdk, setSdk] = useState<DiscordSDK | DiscordSDKMock | null>(null);
  const [user, setUser] = useState<DiscordUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function init() {
      // Check if running in Discord
      const inDiscord = isRunningInDiscord();
      setIsInDiscord(inDiscord);

      if (!inDiscord) {
        setIsLoading(false);
        return;
      }

      // Initialize Discord SDK
      try {
        const result = await initializeDiscordSdk();

        if (result) {
          setSdk(result.sdk);
          setUser(result.auth.user);
          setAccessToken(result.auth.access_token);
          setIsAuthenticated(true);
        } else {
          setError("Failed to initialize Discord SDK");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setIsLoading(false);
      }
    }

    init();
  }, []);

  const setActivity = useCallback(async (details: string, state?: string) => {
    if (isInDiscord) {
      await setDiscordActivity(details, state);
    }
  }, [isInDiscord]);

  return (
    <DiscordContext.Provider
      value={{
        isInDiscord,
        isLoading,
        isAuthenticated,
        sdk,
        user,
        accessToken,
        error,
        setActivity,
      }}
    >
      {children}
    </DiscordContext.Provider>
  );
}
