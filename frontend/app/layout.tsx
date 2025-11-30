import type { Metadata } from "next";
import { Orbitron, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const orbitron = Orbitron({
  variable: "--font-orbitron",
  subsets: ["latin"],
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sentinel Orchestrator Network",
  description: "Governance Guard for the Cardano Era",
};

import { Navbar } from "@/components/Navbar";
import SmoothScroll from "@/components/SmoothScroll";
import { CustomCursor } from "@/components/CustomCursor";
import { PageTransition } from "@/components/PageTransition";

import { WalletProvider } from "@/context/WalletContext";

// ... imports

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${orbitron.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} antialiased bg-obsidian-core text-ghost-white`}
      >
        <WalletProvider>
          <SmoothScroll>
            <CustomCursor />
            <Navbar />
            <PageTransition>
              {children}
            </PageTransition>
          </SmoothScroll>
        </WalletProvider>
      </body>
    </html>
  );
}
