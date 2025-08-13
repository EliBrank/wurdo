"use client";

import {
  createContext,
  SetStateAction,
  use,
  useContext,
  useState,
} from "react";

interface GameContext {
  currentScore?: number;
  setCurrentScore?: React.Dispatch<SetStateAction<number>>;
  wordScore?: number;
  setWordScore?: React.Dispatch<SetStateAction<number>>;
  totalScore?: number;
  setTotalScore?: React.Dispatch<SetStateAction<number>>;
  startWord?: string;
  setStartWord?: React.Dispatch<SetStateAction<string>>;
}

export const GameContext = createContext<GameContext>({});

export function GameContextWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const [currentScore, setCurrentScore] = useState(0);
  const [totalScore, setTotalScore] = useState(0);
  const [wordScore, setWordScore] = useState(0);
  const [startWord, setStartWord] = useState("free");

  return (
    <GameContext.Provider
      value={{
        currentScore,
        setCurrentScore,
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
