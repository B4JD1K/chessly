"use client";

import { SessionProvider } from "next-auth/react";
import { ReactNode } from "react";
import { DiscordProvider } from "@/contexts/discord-context";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <SessionProvider>
      <DiscordProvider>{children}</DiscordProvider>
    </SessionProvider>
  );
}
