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
        ${isBackspace ? 'flex-[2]' : 'flex-[1]'} tile-purple
        active:translate-y-1 active:shadow-none select-none
      `}
    >
      {label}
    </button>
  );
}
