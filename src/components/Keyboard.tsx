import { KeyboardRow } from "./KeyboardRow";

type KeyboardProps = {
  onKeyPress: (key: string) => void;
  onBackspace: () => void;
}

export const Keyboard = ({
  onKeyPress,
  onBackspace
} : KeyboardProps) => {
  // Full letter array used to populate keyboard
  const keyboardLayout: string[][] = [
    ['Q','W','E','R','T','Y','U','I','O','P'],
    ['A','S','D','F','G','H','J','K','L'],
    ['Z','X','C','V','B','N','M'],
  ];

  return (
    <div className="mt-auto space-y-4">
      {keyboardLayout.map((row, index) => (
        <KeyboardRow
          // Key is just for map method
          key={index}
          // Keys are for actual labels in keyboard
          keys={row}
          rowIndex={index}
          // Calculate isLastRow dynamically
          // Last row will contain backspace
          isLastRow={index === keyboardLayout.length - 1}
          onKeyPress={onKeyPress}
          onBackspace={onBackspace}
        />
      ))}
    </div>
  );
}
