import React from "react";
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
import { WebSocketProvider } from "@/components/shared/WebSocketProvider";
import { AgentStatusBadge } from "@/components/shared/AgentStatusBadge";
import { motion } from "framer-motion";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

const Breadcrumb = () => {
  "use client";
  const { usePathname } = require("next/navigation");
  const pathname = usePathname();

  const getBreadcrumbs = (path: string) => {
    const segments = path.split('/').filter(Boolean);
    const breadcrumbs: Array<{ label: string; href: string; icon?: React.ComponentType<any> }> = [{ label: 'Home', href: '/', icon: Home }];

    let currentPath = '';
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === segments.length - 1;

      let label = segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ');

      // Custom labels for specific routes
      if (segment === 'dashboard') label = 'Scanner';
      if (segment === 'governance') label = 'Governance';
      if (segment === 'find-drep') label = 'Find DRep';
      if (segment === 'about') label = 'Protocol';

      // Add "Analysis" for governance sub-routes or when analyzing
      if (segment === 'governance' && isLast) {
        breadcrumbs.push({ label: 'Analysis', href: currentPath });
      } else {
        breadcrumbs.push({ label, href: currentPath });
      }
    });

    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs(pathname);

  if (pathname === '/') return null;

  return (
    <motion.nav
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-20 left-0 right-0 z-40 flex justify-center px-4 pointer-events-none"
    >
      <div className="pointer-events-auto bg-black/20 backdrop-blur-md border border-white/10 rounded-full px-6 py-2 flex items-center gap-2 text-sm">
        {breadcrumbs.map((crumb, index) => (
          <React.Fragment key={crumb.href}>
            {index > 0 && <ChevronRight className="w-3 h-3 text-white/40" />}
            {index === breadcrumbs.length - 1 ? (
              <span className="text-neon-orchid font-medium">{crumb.label}</span>
            ) : (
              <Link
                href={crumb.href}
                className="text-white/60 hover:text-white transition-colors flex items-center gap-1"
              >
                {crumb.icon && <crumb.icon className="w-3 h-3" />}
                {crumb.label}
              </Link>
            )}
          </React.Fragment>
        ))}
      </div>
    </motion.nav>
  );
};

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
        <WebSocketProvider>
          <SmoothScroll>
            <CustomCursor />
            <Navbar />
            <Breadcrumb />
            {/* Agent Status Indicator - Top Right */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="fixed top-6 right-6 z-50"
            >
              <AgentStatusBadge />
            </motion.div>
            <PageTransition>
              {children}
            </PageTransition>
          </SmoothScroll>
        </WebSocketProvider>
      </body>
    </html>
  );
}
