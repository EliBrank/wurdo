"use client";
import React from "react";
import Navbar from "@/src/components/Navbar";
import Link from "next/link";

export default function SettingsPage() {
  return (
    <div>
      <Navbar />
      <main className="container mx-auto p-4">
        {/* Desktop-only message */}
        <div className="hidden md:flex space-x-6 font-medium">
          <p>
            Würdo was designed for mobile devices. Please use a mobile device to
            enjoy. Desktop coming soon!
          </p>
        </div>
        {/* Page Content */}
        <section>
          <p>Game Play coming soon!</p>
          <Link href="/">Back</Link>
        </section>
      </main>
    </div>
  );
}
