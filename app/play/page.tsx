import React from "react";
import Navbar from "@/src/components/Navbar";
import { GameArea } from "@/src/components/GameArea";
import ScoreArea from "@/src/components/ScoreArea";
// import Link from "next/link";

export default function PlayPage() {
  return (
    <div className="flex h-full flex-col">
      <main className="xs:p-4 flex flex-1 flex-col bg-primary-light p-2">
        {/* Desktop-only message */}
        <div className="hidden space-x-6 font-medium md:flex">
          <p>
            Würdo was designed for mobile devices. Please use a mobile device to
            enjoy. Desktop coming soon!
          </p>
        </div>
        {/* Page Content */}
        <section className="h-full">
          <ScoreArea currentScore={8} maxScore={10} />
          <GameArea />
        </section>
      </main>
    </div>
  );
}
