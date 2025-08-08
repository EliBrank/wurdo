import React from "react";

type GameModeButtonProps = {
  label: string;
  href?: string;
  disabled?: boolean;
  ariaLabel?: string;
  onClick?: () => void;
};

export default function GameModeButton({
  label,
  href,
  disabled = false,
  ariaLabel,
  onClick,
}: GameModeButtonProps) {
  const baseClasses =
    "inline-block text-center px-4 py-2 my-4 text-5xl font-family-inter min-w-80 h-20 bg-(--green-main) text-white rounded-lg hover:opacity-90 shadow-[0_4px_0_0_#587F5F] transition-all";

  const activeClasses = disabled
    ? ""
    : "active:translate-y-1 active:shadow-[0_2px_0_0_#587F5F]";

  const handleClick = () => {
    if (disabled) return;

    if (onClick) {
      onClick();
    } else if (href) {
      window.location.href = href;
    }
  };

  // Handle keyboard accessibility allows activation with Enter or Space keys
  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleClick();
    }
  };

  return (
    <button
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={`${baseClasses} ${activeClasses}`}
      disabled={disabled}
      aria-label={ariaLabel || label}
      aria-disabled={disabled}
      type="button"
    >
      {label}
    </button>
  );
}
