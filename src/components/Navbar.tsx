import React, { useState } from "react";
import Link from "next/link";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="p-4 bg-(--purple-main) text-white">
      <div className="container mx-auto flex justify-between items-center">
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
        <ul className="md:hidden mt-2 p-4 space-y-2">
          <li></li>
          <li>
            <a href="/about">About</a>
          </li>
          <li>
            <a href="/contact">Contact</a>
          </li>
          <li>
            <a href="/settings">Settings</a>
          </li>
        </ul>
      )}
    </nav>
  );
}
