"use client";

import { DiscordSDK, DiscordSDKMock } from "@discord/embedded-app-sdk";

export type DiscordUser = {
  id: string;
  username: string;
  discriminator: string;
  avatar: string | null;
  global_name: string | null;
};

export type DiscordAuth = {
  access_token: string;
  user: DiscordUser;
  scopes: string[];
  expires: string;
};

let discordSdk: DiscordSDK | DiscordSDKMock | null = null;

export function isRunningInDiscord(): boolean {
  if (typeof window === "undefined") return false;

  // Check if we're in an iframe (Discord Activity runs in iframe)
  const isIframe = window.self !== window.top;

  // Check for Discord-specific URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const hasDiscordParams = urlParams.has("frame_id") || urlParams.has("instance_id");

  return isIframe && hasDiscordParams;
}

export async function getDiscordSdk(): Promise<DiscordSDK | DiscordSDKMock | null> {
  if (typeof window === "undefined") return null;

  if (discordSdk) return discordSdk;

  const clientId = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID;

  if (!clientId) {
    console.error("NEXT_PUBLIC_DISCORD_CLIENT_ID is not set");
    return null;
  }

  // Check if we should use mock (for local development)
  const useMock = process.env.NEXT_PUBLIC_DISCORD_SDK_MOCK === "true";

  if (useMock) {
    discordSdk = new DiscordSDKMock(clientId, null as any, null as any, null as any);
  } else {
    discordSdk = new DiscordSDK(clientId);
  }

  return discordSdk;
}

export async function initializeDiscordSdk(): Promise<{
  sdk: DiscordSDK | DiscordSDKMock;
  auth: DiscordAuth;
} | null> {
  const sdk = await getDiscordSdk();

  if (!sdk) return null;

  try {
    // Wait for SDK to be ready
    await sdk.ready();

    // Authorize with Discord
    const { code } = await sdk.commands.authorize({
      client_id: process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID!,
      response_type: "code",
      state: "",
      prompt: "none",
      scope: ["identify", "guilds"],
    });

    // Exchange code for access token via our backend
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/discord/activity`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to exchange Discord code");
    }

    const auth: DiscordAuth = await response.json();

    // Authenticate with Discord SDK
    await sdk.commands.authenticate({
      access_token: auth.access_token,
    });

    return { sdk, auth };
  } catch (error) {
    console.error("Failed to initialize Discord SDK:", error);
    return null;
  }
}

export async function setDiscordActivity(details: string, state?: string): Promise<void> {
  const sdk = await getDiscordSdk();
  if (!sdk || sdk instanceof DiscordSDKMock) return;

  try {
    await sdk.commands.setActivity({
      activity: {
        type: 0, // Playing
        details,
        state,
      },
    });
  } catch (error) {
    console.error("Failed to set Discord activity:", error);
  }
}
