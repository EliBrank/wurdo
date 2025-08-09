"use client";

import { useState } from "react";
import { Keyboard } from "./Keyboard";

export const GameArea = () => {
  const [wordInput, setWordInput] = useState<string>('');
  const minWordLength = 3, maxWordLength = 7;

  // EVENT HANDLERS
  const handleKeyPress = (key: string) => {
    if (wordInput.length < maxWordLength) {
      setWordInput(prev => prev + key);
    }
  }
  const handleBackspace = () => {
    // Removes one letter from word input
    setWordInput(prev => prev.slice(0, -1));
  }
  const handleSubmit = () => {
    // Check if word is between 3 and 7 letters
    if (wordInput.length > minWordLength && wordInput.length < maxWordLength) {
      // TODO: connect to word scoring service
    }
  }

  return (
    <div className="h-full bg-amber-400">
      <Keyboard
        onKeyPress={handleKeyPress}
        onBackspace={handleBackspace}
      />
    </div>
  );
}
