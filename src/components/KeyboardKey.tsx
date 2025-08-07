type KeyboardKeyProps = {
  label: string;
  isBackspace?: boolean;
  onClick: () => void;
}

export const KeyboardKey = ({
  label,
  isBackspace = false,
  onClick
} : KeyboardKeyProps) => {
  return (
    <button
      onClick={onClick}
      className={`
        ${isBackspace ? 'col-span-2' : 'col-span-1'}
        h-12 touch-manipulation rounded-md
        bg-secondary text-lg font-semibold
        select-none
      `}
    >
      {label}
    </button>
  );
}
