"use client";
import React from "react";
import Link from "next/link";
import Navbar from "@/src/components/Navbar";

export default function ContactPage() {
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
          <h2 className="text-2xl font-bold text-white">Contact</h2>
          <p className="md:hidden mt-2 p-4 space-y-2 rounded-3xl bg-(--background)">
            Würdo was created as a capstone project by students Kelci Atkinson,
            Elias Brinkman, Isaac Edwards, Danny McGeough, and Nathan Rhys. You
            find our Github repo{" "}
            <Link
              className="font-bold"
              href="https://github.com/EliBrank/wurdo"
            >
              here
            </Link>
            .
          </p>
        </section>
      </main>
    </div>
  );
}
