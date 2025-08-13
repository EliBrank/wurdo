import type { Metadata } from "next";
import { GameContextWrapper } from "@/context";

import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="h-screen antialiased">
        <GameContextWrapper> {children}</GameContextWrapper>
      </body>
    </html>
  );
}
