"use client";
import React from "react";
import Navbar from "@/src/components/Navbar";
import Footer from "@/src/components/Footer";

export default function AboutPage() {
  return (
    <div>
      <Navbar />
      <main className="container min-h-screen mx-auto p-4">
        {/* Desktop-only message */}
        <div className="hidden md:flex space-x-6 font-medium">
          <p>
            Würdo was designed for mobile devices. Please use a mobile device to
            enjoy. Desktop coming soon!
          </p>
        </div>
        {/* Page Content */}
        <section>
          <h2 className="text-2xl font-bold text-white">About</h2>
          <p className="md:hidden mt-2 p-4 space-y-2 rounded-3xl bg-(--background)">
            Würdo is a daily word ladder challenge where puzzle is unique. Play
            words that are one letter off, rhyme, or are anagrams to earn
            points. But be careful — once your energy bar runs out, the game is
            over!
          </p>
        </section>
      </main>
      <Footer />
    </div>
  );
}
