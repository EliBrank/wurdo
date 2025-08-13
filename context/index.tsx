"use client";

import {
  createContext,
  SetStateAction,
  use,
  useContext,
  useState,
} from "react";

interface GameContext {
  wordScore?: number;
  setWordScore?: React.Dispatch<SetStateAction<number>>;
  totalScore?: number;
  setTotalScore?: React.Dispatch<SetStateAction<number>>;
  startWord?: string;
  setStartWord?: React.Dispatch<SetStateAction<string>>;
  wordHistory?: string[];
  setWordHistory?: React.Dispatch<SetStateAction<string[]>>;
  gameOver?: boolean;
  setGameOver?: React.Dispatch<SetStateAction<boolean>>;
  turns?: number;
  setTurns?: React.Dispatch<SetStateAction<number>>;
}

export const GameContext = createContext<GameContext>({});

export function GameContextWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const [wordHistory, setWordHistory] = useState<string[]>([]);
  const [totalScore, setTotalScore] = useState(0);
  const [wordScore, setWordScore] = useState(0);
  const [startWord, setStartWord] = useState("free");
  const [gameOver, setGameOver] = useState(false);
  const [turns, setTurns] = useState(10);

  return (
    <GameContext.Provider
      value={{
        wordHistory,
        setWordHistory,
        wordScore,
        setWordScore,
        totalScore,
        setTotalScore,
        startWord,
        setStartWord,
        gameOver,
        setGameOver,
        turns,
        setTurns,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGameContext() {
  return useContext(GameContext);
}
