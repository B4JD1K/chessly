import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { ActivityLayout } from "@/components/activity-layout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Chessly - Chess Puzzle Trainer",
  description: "Daily chess puzzles to improve your game",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <ActivityLayout>{children}</ActivityLayout>
        </Providers>
      </body>
    </html>
  );
}
