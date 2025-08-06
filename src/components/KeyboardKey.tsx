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
        ${isBackspace ? 'col-span-2' : ''}
      `}
    >
      {label}
    </button>
  );
}
