"use client";

import { useState } from "react";
import { Keyboard } from "./Keyboard";
import { WordInput } from "./WordInput";
import { WordHistory } from "./WordHistory";

export const GameArea = () => {
  const [typedWord, setTypedWord] = useState<string>('');
  const minWordLength = 3, maxWordLength = 7;

  // EVENT HANDLERS
  const handleKeyPress = (key: string) => {
    if (typedWord.length < maxWordLength) {
      setTypedWord(prev => prev + key);
    }
  }
  const handleBackspace = () => {
    // Removes one letter from word input
    setTypedWord(prev => prev.slice(0, -1));
  }
  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   // Preliminary check if word is between 3 and 7 letters
  //   if (typedWord.length > minWordLength && typedWord.length < maxWordLength) {
  //     // TODO: connect to word scoring service
  //   }
  // }

  return (
    <div className="flex h-full flex-col pb-2">
      <WordHistory />
      <div className="mt-auto">
        <WordInput
          typedWord={typedWord}
        />
        <Keyboard
          onKeyPress={handleKeyPress}
          onBackspace={handleBackspace}
        />
      </div>
    </div>
  );
}
