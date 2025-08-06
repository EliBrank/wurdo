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
    setWordInput(prev => prev.slice(0, -1));
  }
  const handleSubmit = () => {
    if (wordInput.length > minWordLength && wordInput.length < maxWordLength) {
      // TODO: connect to word scoring service
    }
  }

  return (
    <div>
      <Keyboard
        onKeyPress={}
        onBackspace={}
      />
    </div>
  );
}
