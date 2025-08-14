"use client";

import { useGameContext } from "@/context";
import { startGame } from "@/lib/gsActions";
import { useEffect, useState, useContext } from "react";
export default function PlayLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { startWord } = useGameContext();
  if (!startWord) return "hello";
  return (
    useEffect(() => {
      startGame(startWord);
    }, []),
    (
      <div className="flex h-full flex-col">
        <main className="xs:p-4 flex flex-1 flex-col bg-primary-light p-2">
          {/* Desktop-only message */}
          <div className="hidden space-x-6 font-medium md:flex">
            <p>
              Würdo was designed for mobile devices. Please use a mobile device
              to enjoy. Desktop coming soon!
            </p>
          </div>
          {/* Page Content */}
          <section className="h-full">{children}</section>
        </main>
      </div>
    )
  );
}
