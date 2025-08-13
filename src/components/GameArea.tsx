"use client";

import { useState } from "react";
import { Keyboard } from "./Keyboard";
import { WordInput } from "./WordInput";
import { WordHistory } from "./WordHistory";

export const GameArea = () => {
  const [typedWord, setTypedWord] = useState<string>('');
  const [wordHistory, setWordHistory] = useState<string[]>([]);

  const minWordLength = 3, maxWordLength = 7;

  // EVENT HANDLERS
  const handleKeyPress = (letter: string) => {
    // Add letter of pressed key (as long as word hasn't reached max length)
    if (typedWord.length < maxWordLength) {
      setTypedWord(prev => prev + letter);
    }
  }

  const handleBackspace = () => {
    // Removes one letter from word input
    setTypedWord(prev => prev.slice(0, -1));
  }

  const handleSubmit = async () => {
    // Preliminary check if word is between 3 and 7 letters
    if (typedWord.length < minWordLength || typedWord.length > maxWordLength) {
      return;
    }
    if (wordHistory.includes(typedWord)) {
      return;
    }
    // TODO: connect to word scoring service
    const wordValidation = await getWordData(typedWord);
    if (!wordValidation) return;

    setWordHistory(prev => [...prev, typedWord]);
    setTypedWord('');
  }

  return (
    <div className="mt-auto flex flex-col pb-2">
      <WordHistory words={wordHistory} />
      <div className="mt-16">
        <WordInput
          typedWord={typedWord}
          onSubmit={handleSubmit}
        />
        <Keyboard
          onKeyPress={handleKeyPress}
          onBackspace={handleBackspace}
        />
      </div>
    </div>
  );
}

// FIX: Temporary function - remove later
async function getWordData(word: string) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(word.trim().length > 0)
    }, 100)
  });
}
