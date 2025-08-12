import { KeyboardTile } from "./KeyboardTile";

type KeyboardRowProps = {
  keys: string[];
  rowIndex: number;
  isLastRow?: boolean;
  onKeyPress: (key: string) => void;
  onBackspace?: () => void;
}

export const KeyboardRow = ({
  keys,
  rowIndex,
  isLastRow = false,
  onKeyPress,
  onBackspace,
} : KeyboardRowProps) => {
  // +bool treats true/false as 1/0
  // make last row 2 units longer because it has backspace
  // const rowWidth = (keys.length + (+isLastRow * 2)) * 10
  const rowClasses = [
    '',
    'max-w-[90%] mx-auto flex gap-1',
    'max-w-[90%] justify-end ml-auto flex gap-1',
  ];
  const thisRowClasses = `${rowClasses[rowIndex]} flex gap-1`;

  return (
    <div className={thisRowClasses}>
      {keys.map((key) => (
        <KeyboardTile
          key={key}
          label={key}
          onClick={() => onKeyPress(key)}
        />
      ))}
      {isLastRow && onBackspace && (
        <KeyboardTile
          label={'⌫'}
          isBackspace
          onClick={onBackspace}
        />
      )}
    </div>
  );
}
