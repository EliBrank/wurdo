import { KeyboardKey } from "./KeyboardKey";

type KeyboardRowProps = {
  keys: string[];
  isLastRow: boolean;
  onKeyPress: (key: string) => void;
  onBackspace?: () => void;
}

export const KeyboardRow = ({
  keys,
  isLastRow = false,
  onKeyPress,
  onBackspace
} : KeyboardRowProps) => {
  return (
    <div className="align-items-center order-first mx-auto grid grid-cols-10 justify-center gap-1">
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
