"use client";

import { useState } from "react";
import { Keyboard } from "./Keyboard";
import { WordInput } from "./WordInput";
import { WordHistory } from "./WordHistory";
import { playGame } from "@/lib/gsActions";
import { useGameContext } from "@/context";

export const GameArea = () => {
  const [typedWord, setTypedWord] = useState<string>("");
  const [wordHistory, setWordHistory] = useState<string[]>([]);
  const { setWordScore, setTotalScore } = useGameContext();
  const { turns, setTurns } = useGameContext();
  const { gameOver, setGameOver } = useGameContext();

  if (!setWordScore) return;
  if (!setTotalScore) return;
  if (!setTurns) return;
  if (!turns) return 10;
  if (!setGameOver) return;

  const minWordLength = 3,
    maxWordLength = 7;

  // EVENT HANDLERS
  const handleKeyPress = (letter: string) => {
    // Add letter of pressed key (as long as word hasn't reached max length)
    if (typedWord.length < maxWordLength) {
      setTypedWord((prev) => prev + letter);
    }
  };

  const handleBackspace = () => {
    // Removes one letter from word input
    setTypedWord((prev) => prev.slice(0, -1));
  };

  const handleSubmit = async () => {
    if (turns <= 0 || gameOver) {
      return;
    }

    if (typedWord.length < minWordLength || typedWord.length > maxWordLength)
      return;
    if (wordHistory.includes(typedWord)) return;

    const wordValidation = await playGame(typedWord.toLowerCase());

    // If the server says it's a duplicate or invalid word
    if (
      wordValidation.status !== "move_processed" ||
      !wordValidation?.player_result?.data
    ) {
      console.warn(
        "Invalid move:",
        wordValidation.error || wordValidation.status
      );
      return;
    }

    const wordScoreValue = Math.round(
      wordValidation.player_result.data.total_score
    );
    setWordScore(wordScoreValue);
    setTotalScore((prev) => prev + wordScoreValue);

    setWordHistory((prev) => [...prev, typedWord]);
    setTypedWord("");

    const roundTurns = turns - 1;
    setTurns(roundTurns);
    if (roundTurns === 0) {
      setGameOver(true);
    }
  };

  return (
    <div className="mt-auto flex flex-col pb-2">
      <WordHistory words={wordHistory} />
      <div className="mt-50">
        <WordInput typedWord={typedWord} onSubmit={handleSubmit} />
        <Keyboard onKeyPress={handleKeyPress} onBackspace={handleBackspace} />
      </div>
    </div>
  );
};
