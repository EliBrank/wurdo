"use client";

import React, { useState } from "react";
import Link from "next/link";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-(--purple-main) p-4 text-white">
      <div className="container mx-auto flex items-center justify-between">
        {/* Logo */}
        {/* Put logo here instead of h1? */}
        <h1 className="font-bold ">
          <Link href="/">würdo</Link>
        </h1>

        {/* Mobile Menu Button */}
        <button className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
          ☰
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <ul className="mt-2 space-y-2 p-4 md:hidden">
          <li></li>
          <li>
            <Link href="/about">About</Link>
          </li>
          <li>
            <Link href="/contact">Contact</Link>
          </li>
          <li>
            <Link href="/settings">Settings</Link>
          </li>
        </ul>
      )}
    </nav>
  );
}
