"use client";

import { createContext, SetStateAction, useContext, useState } from "react";

interface GameContext {
  currentScore?: number;
  setCurrentScore?: React.Dispatch<SetStateAction<number>>;
  maxScore?: number;
  setMaxScore?: React.Dispatch<SetStateAction<number>>;
  startWord?: string;
  setStartWord?: React.Dispatch<SetStateAction<string>>;
}

export const GameContext = createContext<GameContext>({});

export function GameContextWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const [wordScore, setWordScore] = useState(0);
  const [totalScore, setTotalScore] = useState(0);
  const [startWord, setStartWord] = useState("free");

  return (
    <GameContext.Provider
      value={{
        wordScore,
        setWordScore,
        totalScore,
        setTotalScore,
        startWord,
        setStartWord,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGameContext() {
  return useContext(GameContext);
}
