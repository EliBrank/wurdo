import React from "react";
import Navbar from "@/src/components/Navbar";
import { GameArea } from "@/src/components/GameArea";
// import Link from "next/link";

export default function PlayPage() {
  return (
    <div className="flex h-full flex-col">
      <Navbar />
      <main className="container mx-auto flex flex-1 flex-col bg-blue-200 p-4">
        {/* Desktop-only message */}
        <div className="hidden space-x-6 font-medium md:flex">
          <p>
            Würdo was designed for mobile devices. Please use a mobile device to
            enjoy. Desktop coming soon!
          </p>
        </div>
        {/* Page Content */}
        <section className="mt-auto">
          <GameArea />
        </section>
      </main>
    </div>
  );
}
