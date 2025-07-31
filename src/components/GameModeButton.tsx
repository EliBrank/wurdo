import React from "react";

type GameModeButtonProps = {
  label: string;
  href?: string;
};

export default function GameModeButton({ label, href }: GameModeButtonProps) {
  const baseClasses =
    "px-4 py-2 bg-(--green-main) text-white rounded-lg hover:opacity-90 transition";

  if (href) {
    return (
      <a href={href} className={baseClasses}>
        {label}
      </a>
    );
  }
}
