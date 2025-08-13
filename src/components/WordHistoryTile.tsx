type WordHistoryTileProps = {
  label: string;
}

export const WordHistoryTile = ({
  label,
} : WordHistoryTileProps) => {

  return (
    <span
      className='tile-green col-span-1 flex items-center justify-center select-none'
    >
      {label}
    </span>
  );
}
