"use client";
import React from "react";
import Navbar from "@/src/components/Navbar";

export default function AboutPage() {
  return (
    <div>
      <Navbar />
      <main className="container mx-auto p-4">
        <div className="hidden md:flex space-x-6 font-medium">
          <p>
            würdo was designed for mobile. Please use a mobile device to enjoy.
            Desktop coming soon!
          </p>
        </div>
        <div>
          <p className="md:hidden mt-2 p-4 space-y-2">
            würdo is a word ladder game with a daily unique challenge. Words
            that are one-letter-off, rhymes, or anagrams can be played to earn
            points. Run out of your energy bar and the game is over!
          </p>
        </div>
      </main>
    </div>
  );
}
