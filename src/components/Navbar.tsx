import React, { useState } from "react";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="p-4 bg-amber-300">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo */}
        {/* Put logo here instead of h1? */}
        <h1 className="font-bold">würdo</h1>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-black"
          onClick={() => setIsOpen(!isOpen)}
        >
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
            <a href="/services">Contact</a>
          </li>
          <li>
            <a href="/contact">Settings</a>
          </li>
        </ul>
      )}
    </nav>
  );
}
