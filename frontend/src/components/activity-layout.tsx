"use client";

import { ReactNode } from "react";
import { useDiscord } from "@/contexts/discord-context";
import { Header } from "@/components/header";
import { Loader2 } from "lucide-react";

interface ActivityLayoutProps {
  children: ReactNode;
}

export function ActivityLayout({ children }: ActivityLayoutProps) {
  const { isInDiscord, isLoading, error } = useDiscord();

  // Show loading state while checking Discord context
  if (isLoading && isInDiscord) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-500" />
          <p className="mt-4 text-gray-400">Łączenie z Discordem...</p>
        </div>
      </div>
    );
  }

  // Show error if Discord initialization failed
  if (error && isInDiscord) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center max-w-md px-4">
          <div className="text-red-500 text-xl mb-2">⚠️</div>
          <h2 className="text-lg font-semibold text-white mb-2">Błąd połączenia</h2>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  // In Discord Activity mode - no header, optimized UI
  if (isInDiscord) {
    return (
      <div className="min-h-screen bg-gray-900 text-white">
        {children}
      </div>
    );
  }

  // Normal web mode - show header
  return (
    <>
      <Header />
      <main>{children}</main>
    </>
  );
}
