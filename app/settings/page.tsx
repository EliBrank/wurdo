"use client";
import React from "react";
import Navbar from "@/src/components/Navbar";
import Footer from "@/src/components/Footer";

export default function SettingsPage() {
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
          <h3 className="text-2xl font-bold text-white">Settings</h3>
          <ul>
            <li>Dark/Light mode</li>
            <li>Music</li>
            <li>Sound Effects</li>
          </ul>
        </section>
      </main>
      <Footer />
    </div>
  );
}
