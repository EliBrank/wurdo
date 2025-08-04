import React from "react";

type GameModeButtonProps = {
  label: string;
  href?: string;
};

export default function GameModeButton({ label, href }: GameModeButtonProps) {
  const baseClasses =
    "inline-block text-center px-4 py-2 my-2 min-w-full bg-(--green-main) text-white rounded-lg hover:opacity-90 shadow-[0_4px_0_0_#587F5F] transition-all active:translate-y-1 active:shadow-[0_2px_0_0_#587F5F] active:brightness-95";

  return (
    <button
      onClick={() => (href ? (window.location.href = href) : null)}
      className={baseClasses}
    >
      {label}
    </button>
  );
}
