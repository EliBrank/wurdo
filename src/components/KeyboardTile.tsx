type KeyboardTileProps = {
  label: string;
  isBackspace?: boolean;
  onClick: () => void;
}

export const KeyboardTile = ({
  label,
  isBackspace = false,
  onClick
} : KeyboardTileProps) => {

  return (
    <button
      onClick={onClick}
      className={`
        ${isBackspace ? 'flex-[2]' : 'flex-[1]'} tile-purple
        select-none active:translate-y-1 active:shadow-none
      `}
    >
      {label}
    </button>
  );
}
