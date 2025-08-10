import { KeyboardKey } from "./KeyboardKey";

type KeyboardRowProps = {
  keys: string[];
  isLastRow?: boolean;
  onKeyPress: (key: string) => void;
  onBackspace?: () => void;
}

export const KeyboardRow = ({
  keys,
  isLastRow = false,
  onKeyPress,
  onBackspace,
} : KeyboardRowProps) => {
  // +bool treats true/false as 1/0
  // make last row 2 units longer because it has backspace
  const rowWidth = (keys.length + (+isLastRow * 2)) * 10
  console.log('rowWidth:', rowWidth);

  return (
    <div className={`max-w-[${rowWidth}%] ${isLastRow ? 'justify-end ml-auto' : 'mx-auto'} flex gap-1`}>
      {keys.map((key) => (
        <KeyboardKey
          key={key}
          label={key}
          onClick={() => onKeyPress(key)}
        />
      ))}
      {isLastRow && onBackspace && (
        <KeyboardKey
          label={'⌫'}
          isBackspace
          onClick={onBackspace}
        />
      )}
    </div>
  );
}
