"use client";
import React from "react";
import Navbar from "@/src/components/Navbar";
// import Link from "next/link";

export default function PlayPage() {
  return (
    <div>
      <Navbar />
      <main className="container mx-auto p-4">
        {/* Desktop-only message */}
        <div className="hidden space-x-6 font-medium md:flex">
          <p>
            Würdo was designed for mobile devices. Please use a mobile device to
            enjoy. Desktop coming soon!
          </p>
        </div>
        {/* Page Content */}
        <section>
        </section>
      </main>
    </div>
  );
}
