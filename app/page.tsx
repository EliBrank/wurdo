"use client";
import Navbar from "../src/components/Navbar";
import React from "react";

export default function HomePage() {
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
      </main>
    </div>
  );
}
