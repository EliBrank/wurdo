"use client";
import Navbar from "../src/components/Navbar";
import React from "react";
import GameModeButton from "@/src/components/GameModeButton";
import Footer from "@/src/components/Footer";

export default function HomePage() {
  return (
    <div>
      <Navbar />
      <main className="container mx-auto bg-(--background) p-1 md:p-4">
        <div className="hidden font-medium md:flex">
          <p>
            würdo was designed for mobile. Please use a mobile device to enjoy.
            Desktop coming soon!
          </p>
        </div>
        <section className="flex min-h-screen flex-col items-center py-20 md:hidden">
          <GameModeButton label="Daily" href="/play" />
          <GameModeButton label="Infinite" href="/play" />
          <GameModeButton label="Challenge" href="/play" />
        </section>
      </main>
      <Footer />
    </div>
  );
}
